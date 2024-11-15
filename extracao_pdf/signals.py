from django.db.models.signals import post_save, m2m_changed, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from notifications.signals import notify
from .models import Processo, Card, List, Leilao, EmailLog, EmailTemplate, ChecklistItem, Board, CardsAgregados, Bem
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.contenttypes.models import ContentType
import json
from extracao_pdf.middleware import get_current_user
from django.forms.models import model_to_dict
from extracao_pdf.api_publicacao import publicar_edital


def log_model_changes(instance, action_flag, change_message=''):
    user = get_current_user()
    if not user or not user.is_authenticated:
        return

    LogEntry.objects.log_action(
        user_id=user.pk,
        content_type_id=ContentType.objects.get_for_model(instance).pk,
        object_id=instance.pk,
        object_repr=str(instance),
        action_flag=action_flag,
        change_message=change_message
    )

@receiver(post_save)
def log_model_save(sender, instance, created, **kwargs):
    if isinstance(instance, LogEntry):
        return

    if created:
        log_model_changes(instance, ADDITION, 'Criado')
    else:
        # Logando as mudanças
        old_instance = sender.objects.get(pk=instance.pk)
        old_values = model_to_dict(old_instance)
        new_values = model_to_dict(instance)

        changes = []
        for field, old_value in old_values.items():
            new_value = new_values.get(field)
            if old_value != new_value:
                changes.append(f"{field}: '{old_value}' -> '{new_value}'")

        if changes:
            change_message = "Alterado: " + ", ".join(changes)
            log_model_changes(instance, CHANGE, change_message)

@receiver(post_delete)
def log_model_delete(sender, instance, **kwargs):
    if isinstance(instance, LogEntry):
        return

    log_model_changes(instance, DELETION, 'Deletado')


@receiver(post_save, sender=Processo)
def create_card_for_processo(sender, instance, created, **kwargs):
    if created:
        status_list = List.objects.filter(ordem=0).first()
        if status_list:
            card = Card.objects.create(
                title=instance.numero,
                description="Descrição do processo",
                list=status_list,
                processo=instance,
                responsavel=instance.responsavel,
                vara=instance.vara,
                leilao=instance.leilao,
                leiloeiro=instance.leiloeiro
            )

            # Criação de checklist padrão
            checklist_items = ["Sugestão de datas", "Edital de leilão", "Intimações", "Ofícios"]
            for item in checklist_items:
                ChecklistItem.objects.create(
                    card=card,
                    name=item,
                    completed=False
                )

        if instance.responsavel:
            notify.send(instance, recipient=instance.responsavel, verb='novo processo adicionado',
                        description=f'Processo número {instance.numero} foi adicionado.', target=instance)

@receiver(post_save, sender=Bem)
def update_card_for_alto_valor_bem(sender, instance, **kwargs):
    processo = instance.processo
    try:
        # Tentar obter o card relacionado ao processo
        card = Card.objects.get(processo=processo)

        # Verificar se existe algum bem de alto valor no processo
        bens_alto_valor = Bem.objects.filter(processo=processo, valor__gt=999999.99)

        # Se existir algum bem de alto valor, marca o card como `alto_valor`
        card.alto_valor = bens_alto_valor.exists()
        print(f"Alto valor atualizado para o card: {card.alto_valor} - Processo: {processo.numero}")
        card.save()
    except Card.DoesNotExist:
        pass


@receiver(post_save, sender=Processo)
def update_card_for_processo(sender, instance, created, **kwargs):
    if not created:
        try:
            card = Card.objects.get(processo=instance)
            card.title = instance.numero
            card.vara = instance.vara
            card.leilao = instance.leilao
            card.leiloeiro = instance.leiloeiro

            bens_alto_valor = Bem.objects.filter(processo=instance, valor__gt=999999.99)

            for bem in bens_alto_valor:
                print(f"Bem de alto valor encontrado: {bem.descricao} - Valor: {bem.valor}")

            card.alto_valor = bens_alto_valor.exists()
            print(f"Alto valor atualizado para o card: {card.alto_valor} - Processo: {instance.numero}")
            card.save()

        except Card.DoesNotExist:
            pass


@receiver(post_save, sender=Processo)
def update_leilao_processo_relation(sender, instance, **kwargs):
    if instance.leilao:
        instance.leilao.processos.add(instance)
        instance.leilao.save()


@receiver(m2m_changed, sender=Leilao.processos.through)
def m2m_changed_leilao_processo(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == "post_add" and not reverse:
        for processo_id in pk_set:
            processo = Processo.objects.get(id=processo_id)
    elif action == "post_remove" and not reverse:
        for processo_id in pk_set:
            processo = Processo.objects.get(id=processo_id)


@receiver(post_save, sender=Card)
def send_email_on_card_moved(sender, instance, created, **kwargs):
    if not created:
        previous_card = Card.objects.get(pk=instance.pk)
        if previous_card.list != instance.list:
            email_templates = instance.list.email_templates.all()
            for template in email_templates:
                context = {
                    'card_title': instance.title,
                    'new_phase': instance.list.name,
                }
                message = template.content.format(**context)
                recipients = template.recipients.all()

                for recipient in recipients:
                    try:
                        send_mail(
                            template.subject,
                            message,
                            'noreply@leiloesjudiciais.com.br',
                            [recipient.email],
                            fail_silently=False,
                        )
                        status = 'sent'
                        sent_at = timezone.now()
                    except Exception as e:
                        status = 'failed'
                        sent_at = None
                        print(f"Failed to send email: {e}")

                    EmailLog.objects.create(
                        subject=template.subject,
                        message=message,
                        recipient=recipient.email,
                        status=status,
                        sent_at=sent_at
                    )


@receiver(post_save, sender=Card)
def check_and_create_summary_card(sender, instance, **kwargs):
    target_list_id = 11  # ID do List onde os Cards devem chegar (Fase Finalizada)
    target_board_id = 1  # ID do Board onde os Cards devem estar
    new_board_id = 3  # ID do Board onde o novo Card será criado
    new_list_id = 13  # ID do List onde o novo Card será criado
    cancelado_list_id = 10  # ID da fase cancelado

    processo = instance.processo
    vara = processo.vara if processo else None
    leilao = processo.leilao if processo else None

    # Verificar se vara e leilão estão presentes
    if vara and leilao:
        # Filtrar todos os processos relacionados à vara e leilão, exceto os cancelados
        processos_nao_cancelados = Processo.objects.filter(vara=vara, leilao=leilao).exclude(card__list_id=cancelado_list_id)

        # Verificar se todos os processos não cancelados estão na fase finalizada
        all_finalizados = all(
            card.list.id == target_list_id
            for card in Card.objects.filter(processo__in=processos_nao_cancelados)
        )

        # Se todos os processos não cancelados estão finalizados ou o último foi movido para cancelado
        if all_finalizados or instance.list.id == cancelado_list_id:
            try:
                board_destino = Board.objects.get(id=new_board_id)
                list_destino = List.objects.get(id=new_list_id, board=board_destino)

                # Criar a descrição com a estrutura fornecida
                descricao_completa = """
                <p style="text-align: center;">PODER JUDICIÁRIO&nbsp;</p>
                <p style="text-align: center;">{justica_nome}</p>
                <p style="text-align: center;">{vara_nome}</p>
                <p style="text-align: center;">EDITAL DE LEILÃO E INTIMAÇÃO</p><br>
                <ul>
                """.format(
                    justica_nome=vara.justica.nome.upper() if vara.justica else "JUSTIÇA NÃO DEFINIDA",
                    vara_nome=vara.nome.upper()
                )

                # Adicionar os números dos processos agregados como lista
                for processo_agregado in processos_nao_cancelados:
                    descricao_completa += f'<li style="text-align: left;">{processo_agregado.numero}</li>'

                descricao_completa += "</ul>"
                descricao_completa += '<br><p style="text-align: center;">*** EDITAL NA ÍNTEGRA - ARQUIVO EM PDF - ANEXO ***</p>'

                # Selecionar um processo finalizado para vincular ao card agregado
                processo_para_vincular = processos_nao_cancelados.first()

                # Obter o leiloeiro do processo selecionado
                leiloeiro = processo_para_vincular.leiloeiro if processo_para_vincular else None

                # Verificar se há bens de alto valor
                bens_alto_valor = Bem.objects.filter(processo__in=processos_nao_cancelados, valor__gt=1000000.00).exists()

                # Criar o novo card agregado com o campo `is_aggregated` setado como True
                novo_card = Card.objects.create(
                    title=f"Resumo - Vara {vara.nome}",
                    description=descricao_completa,
                    list=list_destino,
                    leilao=leilao,
                    vara=vara,
                    leiloeiro=leiloeiro,
                    processo=processo_para_vincular,  # Vincula o processo selecionado
                    is_aggregated=True,  # Define que o card é agregado
                    alto_valor=bens_alto_valor  # Define o campo alto_valor se houver bens de alto valor
                )

                # Adicionar os processos finalizados na tabela de agregados
                for proc in processos_nao_cancelados:
                    CardsAgregados.objects.create(card=novo_card, processo=proc)

                checklist_items = [
                    "SOMENTE PUBLICJUD",
                    "JORNAL - DESPACHO",
                    "JORNAL - CLT",
                    "JORNAL - BEM DE ALTO VALOR",
                    "PUBLICAÇÃO VARA",
                    "OUTROS"
                ]
                for item in checklist_items:
                    ChecklistItem.objects.create(
                        card=novo_card,
                        name=item,
                        completed=False
                    )

                print("Card agregado criado com sucesso!")
            except (Board.DoesNotExist, List.DoesNotExist) as e:
                print(f"Erro ao criar card agregado: {e}")
        else:
            print("Nem todos os processos não cancelados estão na fase finalizada.")
    else:
        print("Vara ou Leilão não definidos.")


@receiver(post_save, sender=Card)
def publicar_edital_django(sender, instance, **kwargs):
    # Verifica se já foi publicado e se está na lista correta
    if not instance.publicado and instance.list_id == 25 and instance.list.board_id == 3:
        try:
            print("Tentando publicar edital para o card:", instance.id)
            response = publicar_edital(card=instance)
            print("Resposta da publicação do edital:", response)

        except Exception as e:
            print(f"Erro ao tentar publicar o edital para o card {instance.id}: {e}")

