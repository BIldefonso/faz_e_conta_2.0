from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
]

testes = [
    path('galeria/', views.galeria, name='galeria'),
]


financas = [
    path('financas/dividas', views.alunos_dividas, name='alunos_dividas'),
    path('financas/add_saldo/<int:id_aluno>/', views.add_saldo, name='add_saldo'),
    
    path('financas/comparticipacao', views.comparticipacoes, name='comparticipacoes'),
    path('financas/comparticipacao/add/<int:tipo_transacao>', views.registar_pagamento, name='registar_comparticipacao'),

    path('financas/pagamento/add/', views.registar_pagamento, name='registar_pagamento'),
    path('financas/pagamento/add/<int:id_aluno>/', views.registar_pagamento, name='registar_pagamento'),
    path('financas/pagamento/add/<int:id_aluno>/<int:tipo_transacao>/', views.registar_pagamento, name='registar_pagamento'),
    path('financas/pagamento/add/<int:id_aluno>/<int:tipo_transacao>/<str:valor>/', views.registar_pagamento, name='registar_pagamento'),
]

user = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('user_management/', views.user_management, name='user_management'),
]

alunos = [
]

reports = [
    path('reports/', views.reports, name='reports'),
    path('<str:model>/gerar-pdf/', views.gerar_pdf, name='gerar_pdf'),
    path('gerar-pdf-aluno/<int:aluno_id>/', views.gerar_pdf_aluno, name='gerar_pdf_aluno'),
    path('report/aluno_sala/', views.reportAlunoSala, name='report_aluno_sala'),
    path('gerar-pdf-mensal/', views.reportMensal, name='report_mensal'),
    path('gerar-pdf-mensal/<int:month>/<int:year>/', views.reportMensal, name='report_mensal'),
]

imports = [
    path('export/json', views.export_data_json, name='export_json'),
    path('import/', views.import_data, name='import_data'),
]

backups = [
    path('backup/', views.ver_backup, name='ver_backup'),
    path('backups/create', views.create_backup, name='create_backup'),
    path('backups/restore', views.restore_backup, name='restore_backup'),
]

'''
URLs added
'''
urlpatterns += testes
urlpatterns += user
urlpatterns += reports
urlpatterns += financas
urlpatterns += alunos
urlpatterns += imports
urlpatterns += backups
