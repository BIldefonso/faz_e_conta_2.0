import pytest
from django.utils.timezone import now
from data_hub.models import *

TEST_ALUNO_KWARGS = dict(
        nome_proprio='João',
        apelido='Silva',
        data_admissao=du.timezone.now(),
        data_nascimento=du.timezone.now(),
        data_validade=du.timezone.now(),
        documento='CC',
        numero_documento='12345678',
        morada='Rua Exemplo',
        codigo_postal='1000-000',
        concelho='Lisboa'
)

@pytest.mark.django_db
def test_criacao_aluno():
    obj = Aluno.objects.create(**TEST_ALUNO_KWARGS)
    assert obj.pk is not None

@pytest.mark.django_db
def test_criacao_responsaveleducativo():
    obj = ResponsavelEducativo.objects.create(nome_proprio='Maria',
        apelido='Santos',
        numero_documento=12345678,
        aluno_id=Aluno.objects.create(**TEST_ALUNO_KWARGS))
    assert obj.pk is not None

@pytest.mark.django_db
def test_criacao_alunosaida():
    obj = AlunoSaida.objects.create(aluno_id=Aluno.objects.create(**TEST_ALUNO_KWARGS),
        valencia=AlunoFinacasCalc.objects.create(nome='Sala 1', valencia='Creche'))
    assert obj.pk is not None

@pytest.mark.django_db
def test_criacao_vacinacao():
    obj = Vacinacao.objects.create(aluno_id=Aluno.objects.create(**TEST_ALUNO_KWARGS),
        dose_id=Dose.objects.create(idade=1, obrigatoria=True, periodo_recomendado=12, dose=1, vacina_id=Vacina.objects.create(vacina_name='Vacina A')))
    assert obj.pk is not None

@pytest.mark.django_db
def test_criacao_despesafixa():
    obj = DespesaFixa.objects.create(produto='Renda',
        valor=500.00,
        data=du.timezone.now(),
        fatura=123,
        pagamento='MBWay')
    assert obj.pk is not None

@pytest.mark.django_db
def test_criacao_despesasvariavel():
    obj = DespesasVariavel.objects.create(produto='Material Escolar',
        valor=25.00,
        data=du.timezone.now(),
        fatura=321,
        pagamento='Dinheiro')
    assert obj.pk is not None

# ===============================
# Testes adicionais para functions.py
# ===============================
from data_hub import functions

@pytest.mark.django_db
def test_calcular_rendimento_anual_bruto():
    rendimento = functions.calcular_rendimento_anual_bruto(1000)
    assert rendimento == 12000

@pytest.mark.django_db
def test_calcular_despesas_anuais_fixas():
    despesas = functions.calcular_despesas_anuais_fixas(100)
    assert despesas == 1200

@pytest.mark.django_db
def test_calcular_despesas_mensais_fixas():
    aluno = Aluno.objects.create(**TEST_ALUNO_KWARGS)
    ResponsavelEducativo.objects.create(
        nome_proprio='Maria',
        apelido='Santos',
        numero_documento=1234,
        aluno_id=aluno,
        salario=100
    )
    ResponsavelEducativo.objects.create(
        nome_proprio='Carlos',
        apelido='Ferreira',
        numero_documento=5678,
        aluno_id=aluno,
        salario=100
    )
    despesas = functions.calcular_despesas_mensais_fixas(ResponsavelEducativo.objects.filter(aluno_id=aluno))
    assert despesas == 0

@pytest.mark.django_db
def test_obter_rendimento_anual_bruto():
    aluno = Aluno.objects.create(**TEST_ALUNO_KWARGS)
    ResponsavelEducativo.objects.create(
        nome_proprio='Maria',
        apelido='Santos',
        numero_documento=1234,
        aluno_id=aluno,
        salario=1200
    )
    ResponsavelEducativo.objects.create(
        nome_proprio='Carlos',
        apelido='Ferreira',
        numero_documento=5678,
        aluno_id=aluno,
        salario=1200
    )
    resultado = functions.obter_rendimento_anual_bruto(ResponsavelEducativo.objects.filter(aluno_id=aluno))
    assert resultado == 0



@pytest.mark.django_db
def test_calcular_desconto_mensalidade():
    resultado = functions.calcular_desconto_mensalidade(100, 20)
    assert resultado == 80

# ===============================
# Testes com dados reais para functions.py
# ===============================
import pytest
from django.utils.timezone import now
from data_hub import functions
from data_hub.models import *

@pytest.mark.django_db
def test_calcular_rendimento_anual_bruto():
    aluno = Aluno.objects.create(**TEST_ALUNO_KWARGS)
    resp = ResponsavelEducativo.objects.create(
        nome_proprio='Maria',
        apelido='Santos',
        numero_documento=1234,
        aluno_id=aluno,
        salario=1000
    )
    resultado = functions.calcular_rendimento_anual_bruto(ResponsavelEducativo.objects.filter(pk=resp.pk))
    assert isinstance(resultado, (int, float))

@pytest.mark.django_db
def test_calcular_despesas_anuais_fixas():
    aluno = Aluno.objects.create(**TEST_ALUNO_KWARGS)
    resp = ResponsavelEducativo.objects.create(
        nome_proprio='João',
        apelido='Silva',
        numero_documento=5678,
        aluno_id=aluno
    )
    AlunoFinancas.objects.create(
        aluno_id=aluno,
        ano_letivo='2024/2025',
        agregado=4,
        rendim_líquido=12000,
        despesa_anual=500,
        irs='Sim',
        tax_soc='Não'
    )
    resultado = functions.calcular_despesas_anuais_fixas(ResponsavelEducativo.objects.filter(pk=resp.pk))
    assert resultado == 500

@pytest.mark.django_db
def test_calcular_desconto_mensalidade():
    escalao = EscalaoRendimento.objects.create(nome='1.º', percentagem_mensalidade=50.00)
    aluno = Aluno.objects.create(
        nome_proprio='Luis',
        apelido='Costa',
        data_admissao=now(),
        data_nascimento=now(),
        data_validade=now(),
        documento='CC',
        numero_documento='99999999',
        morada='Rua Y',
        codigo_postal='1000-000',
        concelho='Lisboa',
        escalao=escalao
    )
    resultado = functions.calcular_desconto_mensalidade(aluno.aluno_id)
    assert resultado == 0.5
