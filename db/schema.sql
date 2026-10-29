-- SVS Rastreio — schema de referência para PostgreSQL 16+
-- Gerado automaticamente por scripts/gerar_schema_sql.py.
-- Não edite manualmente: altere backend/app/models.py e regenere.
--
-- Observações:
--   * CPF não existe em texto claro: apenas cpf_hash (HMAC-SHA256 + pepper) e
--     cpf_mascarado.
--   * Posições são append-only; a trilha pública é limitada em consulta.
--   * Para evolução de produção, adote Alembic e habilite PostGIS se for
--     necessário calcular distâncias/rotas no banco.

BEGIN;

CREATE TABLE audit_log (
	id SERIAL NOT NULL, 
	ator_tipo VARCHAR(20) NOT NULL, 
	ator_ref VARCHAR(80), 
	acao VARCHAR(60) NOT NULL, 
	recurso VARCHAR(60) NOT NULL, 
	recurso_id VARCHAR(60), 
	ip_hash VARCHAR(64), 
	detalhe TEXT, 
	criado_em TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);
CREATE INDEX ix_audit_log_acao ON audit_log (acao);
CREATE INDEX ix_audit_log_criado_em ON audit_log (criado_em);

CREATE TABLE municipio (
	id SERIAL NOT NULL, 
	codigo_ibge VARCHAR(7) NOT NULL, 
	nome VARCHAR(120) NOT NULL, 
	uf VARCHAR(2) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (codigo_ibge)
);
CREATE INDEX ix_municipio_nome ON municipio (nome);

CREATE TABLE operadora (
	id SERIAL NOT NULL, 
	nome VARCHAR(120) NOT NULL, 
	cnpj VARCHAR(18), 
	contato VARCHAR(160), 
	ativa BOOLEAN NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (nome)
);

CREATE TABLE motorista (
	id SERIAL NOT NULL, 
	nome VARCHAR(120) NOT NULL, 
	cpf_hash VARCHAR(64) NOT NULL, 
	cpf_mascarado VARCHAR(14) NOT NULL, 
	pin_hash VARCHAR(64) NOT NULL, 
	cnh_categoria VARCHAR(5) NOT NULL, 
	operadora_id INTEGER NOT NULL, 
	ativo BOOLEAN NOT NULL, 
	criado_em TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (cpf_hash), 
	FOREIGN KEY(operadora_id) REFERENCES operadora (id)
);

CREATE TABLE paciente (
	id SERIAL NOT NULL, 
	nome VARCHAR(120) NOT NULL, 
	cpf_hash VARCHAR(64) NOT NULL, 
	cpf_mascarado VARCHAR(14) NOT NULL, 
	data_nascimento DATE NOT NULL, 
	telefone_mascarado VARCHAR(20), 
	municipio_id INTEGER NOT NULL, 
	consentimento_em TIMESTAMP WITHOUT TIME ZONE, 
	ativo BOOLEAN NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(municipio_id) REFERENCES municipio (id)
);
CREATE UNIQUE INDEX ix_paciente_cpf_hash ON paciente (cpf_hash);

CREATE TABLE unidade_saude (
	id SERIAL NOT NULL, 
	nome VARCHAR(160) NOT NULL, 
	tipo VARCHAR(30) NOT NULL, 
	municipio_id INTEGER NOT NULL, 
	latitude FLOAT NOT NULL, 
	longitude FLOAT NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_unidade_tipo CHECK (tipo IN ('UBS', 'UPA', 'HOSPITAL', 'CAPS', 'LABORATORIO', 'CER')), 
	CONSTRAINT ck_unidade_lat CHECK (latitude BETWEEN -90 AND 90), 
	CONSTRAINT ck_unidade_lon CHECK (longitude BETWEEN -180 AND 180), 
	FOREIGN KEY(municipio_id) REFERENCES municipio (id)
);

CREATE TABLE veiculo (
	id SERIAL NOT NULL, 
	placa VARCHAR(8) NOT NULL, 
	modelo VARCHAR(80) NOT NULL, 
	tipo VARCHAR(30) NOT NULL, 
	capacidade INTEGER NOT NULL, 
	acessivel BOOLEAN NOT NULL, 
	ativo BOOLEAN NOT NULL, 
	operadora_id INTEGER NOT NULL, 
	motorista_id INTEGER, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_veiculo_capacidade_positiva CHECK (capacidade > 0), 
	FOREIGN KEY(operadora_id) REFERENCES operadora (id), 
	FOREIGN KEY(motorista_id) REFERENCES motorista (id)
);
CREATE UNIQUE INDEX ix_veiculo_placa ON veiculo (placa);

CREATE TABLE viagem (
	id SERIAL NOT NULL, 
	data DATE NOT NULL, 
	veiculo_id INTEGER NOT NULL, 
	motorista_id INTEGER NOT NULL, 
	origem_municipio_id INTEGER NOT NULL, 
	destino_unidade_id INTEGER, 
	destino_texto VARCHAR(160) NOT NULL, 
	trajeto VARCHAR(15) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	partida_prevista TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	retorno_previsto TIMESTAMP WITHOUT TIME ZONE, 
	iniciada_em TIMESTAMP WITHOUT TIME ZONE, 
	concluida_em TIMESTAMP WITHOUT TIME ZONE, 
	observacao TEXT, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_viagem_status CHECK (status IN ('PLANEJADA', 'AUTORIZADA', 'EM_ANDAMENTO', 'CONCLUIDA', 'CANCELADA')), 
	CONSTRAINT ck_viagem_trajeto CHECK (trajeto IN ('IDA', 'VOLTA', 'IDA_E_VOLTA')), 
	FOREIGN KEY(veiculo_id) REFERENCES veiculo (id), 
	FOREIGN KEY(motorista_id) REFERENCES motorista (id), 
	FOREIGN KEY(origem_municipio_id) REFERENCES municipio (id), 
	FOREIGN KEY(destino_unidade_id) REFERENCES unidade_saude (id)
);
CREATE INDEX ix_viagem_data ON viagem (data);
CREATE INDEX ix_viagem_status ON viagem (status);
CREATE INDEX ix_viagem_veiculo_data ON viagem (veiculo_id, data);
CREATE INDEX ix_viagem_veiculo_id ON viagem (veiculo_id);

CREATE TABLE autorizacao (
	id SERIAL NOT NULL, 
	viagem_id INTEGER NOT NULL, 
	paciente_id INTEGER NOT NULL, 
	numero VARCHAR(40) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	origem VARCHAR(20) NOT NULL, 
	emitida_em TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	validada_em TIMESTAMP WITHOUT TIME ZONE, 
	validada_por VARCHAR(120), 
	PRIMARY KEY (id), 
	CONSTRAINT ck_autorizacao_status CHECK (status IN ('PENDENTE', 'APROVADA', 'NEGADA', 'CANCELADA')), 
	CONSTRAINT ck_autorizacao_origem CHECK (origem IN ('SMS', 'OFICIO', 'SISTEMA')), 
	CONSTRAINT uq_autorizacao_viagem_paciente UNIQUE (viagem_id, paciente_id), 
	FOREIGN KEY(viagem_id) REFERENCES viagem (id) ON DELETE CASCADE, 
	FOREIGN KEY(paciente_id) REFERENCES paciente (id), 
	UNIQUE (numero)
);
CREATE INDEX ix_autorizacao_paciente_id ON autorizacao (paciente_id);
CREATE INDEX ix_autorizacao_status ON autorizacao (status);
CREATE INDEX ix_autorizacao_viagem_id ON autorizacao (viagem_id);

CREATE TABLE evento_viagem (
	id SERIAL NOT NULL, 
	viagem_id INTEGER NOT NULL, 
	tipo VARCHAR(20) NOT NULL, 
	observacao TEXT, 
	ator VARCHAR(120), 
	criado_em TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_evento_tipo CHECK (tipo IN ('INICIO', 'CHEGADA_DESTINO', 'FIM', 'ATRASO', 'INCIDENTE', 'OBSERVACAO')), 
	FOREIGN KEY(viagem_id) REFERENCES viagem (id) ON DELETE CASCADE
);
CREATE INDEX ix_evento_viagem_viagem_id ON evento_viagem (viagem_id);

CREATE TABLE posicao (
	id SERIAL NOT NULL, 
	veiculo_id INTEGER NOT NULL, 
	viagem_id INTEGER, 
	latitude FLOAT NOT NULL, 
	longitude FLOAT NOT NULL, 
	velocidade_kmh FLOAT NOT NULL, 
	rumo FLOAT, 
	precisao_m FLOAT NOT NULL, 
	fonte VARCHAR(20) NOT NULL, 
	capturada_em TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	recebida_em TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_posicao_lat CHECK (latitude BETWEEN -90 AND 90), 
	CONSTRAINT ck_posicao_lon CHECK (longitude BETWEEN -180 AND 180), 
	CONSTRAINT ck_posicao_velocidade CHECK (velocidade_kmh >= 0), 
	CONSTRAINT ck_posicao_fonte CHECK (fonte IN ('APP_MOTORISTA', 'GATEWAY', 'SIMULADOR')), 
	FOREIGN KEY(veiculo_id) REFERENCES veiculo (id), 
	FOREIGN KEY(viagem_id) REFERENCES viagem (id)
);
CREATE INDEX ix_posicao_capturada_em ON posicao (capturada_em);
CREATE INDEX ix_posicao_veiculo_capturada ON posicao (veiculo_id, capturada_em);
CREATE INDEX ix_posicao_veiculo_id ON posicao (veiculo_id);
CREATE INDEX ix_posicao_viagem_id ON posicao (viagem_id);

CREATE TABLE embarque (
	id SERIAL NOT NULL, 
	autorizacao_id INTEGER NOT NULL, 
	embarcado_em TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	desembarcado_em TIMESTAMP WITHOUT TIME ZONE, 
	metodo VARCHAR(15) NOT NULL, 
	registrado_por VARCHAR(120), 
	PRIMARY KEY (id), 
	CONSTRAINT ck_embarque_metodo CHECK (metodo IN ('QRCODE', 'CPF', 'MANUAL')), 
	UNIQUE (autorizacao_id), 
	FOREIGN KEY(autorizacao_id) REFERENCES autorizacao (id) ON DELETE CASCADE
);


COMMIT;
