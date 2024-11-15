from django.contrib import admin
from django.urls import include, path
from extracao_pdf import views as extracao_pdf_views
from django.conf import settings
from django.conf.urls.static import static
from extracao_pdf.views import (ProcessoViewSet, gerar_docx_a_partir_de_html, api_leiloes, kanban_board, kanban_list, \
    calendario, notifications_view, mark_as_read, move_card, add_comment, UserAutocomplete, get_modelos, \
    get_modelos_kanban, LeilaoAutocomplete, admin_relatorios, filtrar_relatorios, download_pdf, download_excel,
                                get_users, update_responsavel, ComarcaAutocomplete, relatorios_view)
from rest_framework import routers


router = routers.DefaultRouter()
router.register('processos', ProcessoViewSet, basename='Processos')

admin.site.site_header = "Administração Central de Processos"
admin.site.site_title = "Site Admin"
admin.site.index_title = "Bem-vindo ao portal de administração"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('extracao_pdf/', include('extracao_pdf.urls')),
    path('pre-visualizacao/', extracao_pdf_views.pre_visualizacao, name='pre_visualizacao'),
    path('confirmar-salvar/', extracao_pdf_views.confirmar_salvar_processo, name='confirmar_salvar_processo'),
    path('', extracao_pdf_views.upload_pdf, name='home'),
    path('processo/escolher-documento/<int:processo_id>/', extracao_pdf_views.escolher_documento, name='escolher_documento'),
    path('processo/gerar-documento/<int:processo_id>/<str:tipo_documento>/', extracao_pdf_views.gerar_documento, name='gerar-documento'),
    path('tinymce/', include('tinymce.urls')),
    path('gerar-docx/<int:modelo_id>/<int:processo_id>/', gerar_docx_a_partir_de_html, name='gerar_docx'),
    path('api/leiloes/', api_leiloes, name='api_leiloes'),
    path('calendario/', calendario, name='calendario'),
    path('', include(router.urls)),
    # path('notificacoes/enviar/', enviar_notificacao_view, name='enviar_notificacao'), # Removido
    path('notifications/', notifications_view, name='notifications'),
    path('notifications/mark_as_read/<int:notification_id>/', mark_as_read, name='mark_as_read'),
    path('kanban/<int:board_id>/', kanban_board, name='kanban_board'),
    path('kanban_list/', kanban_list, name='kanban_list'),
    path('api/move_card/', move_card, name='move_card'),
    path('api/get_processo/<int:card_id>/', extracao_pdf_views.get_processo_details, name='get_processo_details'),
    path('add_comment/<int:card_id>/', extracao_pdf_views.add_comment, name='add_comment'),
    path('user-autocomplete/', UserAutocomplete.as_view(), name='user_autocomplete'),
    path('get_modelos/<int:processo_id>/', get_modelos, name='get_modelos'),
    path('get_arquivos/<int:processo_id>/', extracao_pdf_views.get_arquivos, name='get_arquivos'),
    path('add_checklist_item/<int:card_id>/', extracao_pdf_views.add_checklist_item, name='add_checklist_item'),
    path('toggle_checklist_item/<int:item_id>/', extracao_pdf_views.toggle_checklist_item, name='toggle_checklist_item'),
    path('remove_checklist_item/<int:item_id>/', extracao_pdf_views.remove_checklist_item, name='remove_checklist_item'),
    path('get_checklist/<int:card_id>/', extracao_pdf_views.get_checklist, name='get_checklist'),
    path('get_modelos_kanban/<int:processo_id>/', get_modelos_kanban, name='get_modelos_kanban'),
    path('leilao-autocomplete/', LeilaoAutocomplete.as_view(), name='leilao-autocomplete'),
    path('relatorios/', extracao_pdf_views.admin_relatorios, name='admin_relatorios'),
    path('filtrar-relatorios/', extracao_pdf_views.filtrar_relatorios, name='filtrar_relatorios'),
    path('download-pdf/', download_pdf, name='download_pdf'),
    path('download-excel/', download_excel, name='download_excel'),
    path('get-users/', extracao_pdf_views.get_users, name='get_users'),
    path('update-responsavel/<int:card_id>/', update_responsavel, name='update_responsavel'),
    path('comarca-autocomplete/', ComarcaAutocomplete.as_view(), name='comarca-autocomplete'),
    path('relatorios/board-1/', extracao_pdf_views.admin_relatorios_board_1, name='admin_relatorios_board_1'),
    path('relatorios/board-3/', extracao_pdf_views.admin_relatorios_board_3, name='admin_relatorios_board_3'),
    path('filtrar-relatorios-board-3/', extracao_pdf_views.filtrar_relatorios_board_3, name='filtrar_relatorios_board_3'),
    path('relatorio-simples-board-3/', extracao_pdf_views.relatorio_simples_board_3, name='relatorio_simples_board_3'),
    path('save_publicjud/<int:card_id>/', extracao_pdf_views.save_publicjud, name='save_publicjud'),
    path('dashboard2/', relatorios_view, name='admin-dashboard'),
]


# Serve static and media files from development server
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
