from django.contrib import admin
from django.apps import apps

from data_hub import functions
from .models import *
from django.db.models import Sum
from .admin_filters import *
from django.utils.html import format_html
from django.urls import reverse

class DefaultAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields if not field.primary_key]
        self.ordering = [field.name for field in model._meta.fields if field.name == 'id' and not field.primary_key]
        super().__init__(model, admin_site)

class AlunoAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'escalao_link', 'numero_documento', 'processo', 'saldo', 'sala_nome', 'pgar_mensalidade_link')
    search_fields = ('nome_proprio', 'apelido', 'numero_documento', 'processo')
    list_filter = (SaldoListFilter, 'cuidados_especias', 'sala')
    ordering = [field.name for field in Aluno._meta.fields if not field.primary_key]

    def nome_completo(self, obj):
        return f"{obj.nome_proprio} {obj.apelido}"
    nome_completo.short_description = 'Nome Completo'

    def sala_nome(self, obj):
        # Mostra todas as salas em que o aluno está, separadas por vírgula
        return ", ".join([s.sala_nome for s in obj.sala_set.all()])
    sala_nome.short_description = 'Sala'

    def pgar_mensalidade_link(self, obj):
        valor = functions.calcular_mensalidade_aluno(obj.pk)
        url = reverse('registar_pagamento', args=[obj.pk, 4, valor])
        return format_html('<a href="{}">{}</a>', url, valor)
    pgar_mensalidade_link.short_description = 'Pagar Mensalidade'
    
    def escalao_link(self, obj):
        if obj.escalao_id is None:
            url = functions.atribuir_escalao_aluno(aluno_id= obj.pk)
            return format_html(
                '<span style="color:red;"><a href="{}">Atribuir escalão</a></span>',
                url
            )
        return str(obj.escalao_id)
    escalao_link.short_description = 'Escalão'

class ResponsavelEducativoAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'numero_documento', 'telefone', 'email')
    search_fields = ('nome_proprio', 'apelido', 'numero_documento')
    list_filter = ('concelho',)
    
    def nome_completo(self, obj):
        return f"{obj.nome_proprio} {obj.apelido}"
    nome_completo.short_description = 'Nome Completo'

class TipoProblemaAdmin(admin.ModelAdmin):
    list_display = ('tipo_problema',)
    search_fields = ('tipo_problema',)
    ordering = ('tipo_problema',)

class TipoImagemAdmin(admin.ModelAdmin):
    list_display = ('tipo_imagem',)
    search_fields = ('tipo_imagem',)
    ordering = ('tipo_imagem',)

class DividaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'valor_pagar', 'valor_pago')
    search_fields = ('aluno_id__processo', 'aluno_id__nome_proprio', 'aluno_id__apelido')
    actions = ['agrupar_dividas']

    def aluno(self, obj):
        return f"{obj.aluno_id.nome_proprio} {obj.aluno_id.apelido}"

    aluno.short_description = 'Aluno'

    def agrupar_dividas(self, request, queryset):

        # Agrupa as dívidas selecionadas por aluno
        for aluno_id in queryset.values_list('aluno_id', flat=True).distinct():
            dividas = queryset.filter(aluno_id=aluno_id)
            total_valor_pagar = dividas.aggregate(total=Sum('valor_pagar'))['total'] or 0
            total_valor_pago = dividas.aggregate(total=Sum('valor_pago'))['total'] or 0

        self.message_user(request, "Dívidas agrupadas com sucesso. Veja em Dívida Agrupada.")

    agrupar_dividas.short_description = "Agrupar dívidas selecionadas"


class ImagemAdmin(admin.ModelAdmin):
    list_display = ('alt', 'imagem', 'tipos_imagem')
    search_fields = ('alt',)
    filter_horizontal = ('tipo_imagem_id',)

    def tipos_imagem(self, obj):
        return ", ".join([t.tipo_imagem for t in obj.tipo_imagem_id.all()])
    tipos_imagem.short_description = 'Tipos de Imagem'

class TransacaoAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'data_transacao', 'tipo_transacao', 'valor', 'descricao')
    search_fields = ('aluno_id__pk', 'aluno_id__nome_proprio', 'aluno_id__apelido')
    list_filter = ('data_transacao', 'tipo_transacao')
    def nome_completo(self, obj):
        return f"{obj.aluno_id.nome_proprio} {obj.aluno_id.apelido}"
    
    def tipo_transacao(self, obj):
        if obj.tipo_transacao != None:
            return obj.tipo_transacao.tipo_transacao
    nome_completo.short_description = 'Nome Completo'
    
    tipo_transacao.short_description = 'Tipo de transacao'


admin.site.register(Aluno, AlunoAdmin)
admin.site.register(ResponsavelEducativo, ResponsavelEducativoAdmin)
admin.site.register(TipoProblema, TipoProblemaAdmin)
admin.site.register(TipoImagem, TipoImagemAdmin)
admin.site.register(Divida, DividaAdmin)
admin.site.register(Imagem, ImagemAdmin)
admin.site.register(Transacao, TransacaoAdmin)

models = apps.get_models()
for model in models:
    try:
        admin.site.register(model, type(f"{model.__name__}Admin", (DefaultAdmin,), {
            
        }))
    except admin.sites.AlreadyRegistered:
        # If the model is already registered, skip it
        pass

