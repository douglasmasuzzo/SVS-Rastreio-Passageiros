-- SVS Rastreio — snapshot do cenário sintético (PostgreSQL)
-- Gerado por scripts/exportar_seed_sql.py em 2026-10-29T17:22:15.
-- Data de referência: 2026-10-29.
--
-- AVISO: este arquivo contém hashes gerados com o pepper de DESENVOLVIMENTO.
-- Para qualquer ambiente real, use backend/app/seed.py com segredos próprios
-- ou um processo de migração/carga governado.
--
-- Ordem de carga respeita as chaves estrangeiras. Os IDs são explícitos e as
-- sequências são ajustadas ao final.

BEGIN;

-- municipio: 5 registro(s)
INSERT INTO municipio (id, codigo_ibge, nome, uf) VALUES (1, '3548500', 'Santos', 'SP');
INSERT INTO municipio (id, codigo_ibge, nome, uf) VALUES (2, '3551009', 'São Vicente', 'SP');
INSERT INTO municipio (id, codigo_ibge, nome, uf) VALUES (3, '3513504', 'Cubatão', 'SP');
INSERT INTO municipio (id, codigo_ibge, nome, uf) VALUES (4, '3550308', 'São Paulo', 'SP');
INSERT INTO municipio (id, codigo_ibge, nome, uf) VALUES (5, '3513801', 'Diadema', 'SP');
SELECT setval(pg_get_serial_sequence('municipio', 'id'), (SELECT MAX(id) FROM municipio));

-- operadora: 2 registro(s)
INSERT INTO operadora (id, nome, cnpj, contato, ativa) VALUES (1, 'Transporte Saúde Litoral (demo)', NULL, 'operacao@litoral.exemplo', TRUE);
INSERT INTO operadora (id, nome, cnpj, contato, ativa) VALUES (2, 'Mobilidade Assistencial SP (demo)', NULL, 'operacao@metropolitana.exemplo', TRUE);
SELECT setval(pg_get_serial_sequence('operadora', 'id'), (SELECT MAX(id) FROM operadora));

-- motorista: 4 registro(s)
INSERT INTO motorista (id, nome, cpf_hash, cpf_mascarado, pin_hash, cnh_categoria, operadora_id, ativo, criado_em) VALUES (1, 'Carlos Andrade (demo)', 'c2bd514db58c54644b627ec868ae74c9523421d6204588ce22d04d60bbe301fd', '***.***.***-75', '906df6606b02dd7ea363facc9de0da3f2c215b9921ab7221de458d4edb7cbfd1', 'D', 1, TRUE, '2026-10-29 20:22:15.954192');
INSERT INTO motorista (id, nome, cpf_hash, cpf_mascarado, pin_hash, cnh_categoria, operadora_id, ativo, criado_em) VALUES (2, 'Marina Souza (demo)', '786abc7957cbc0d854c061bba3b95e082da28eef94ed87967ffff03692058913', '***.***.***-56', '223e259d4f5b155a9366b84c3838f74c8a2fdc8f078fed65abe004ddc8fd5b94', 'D', 1, TRUE, '2026-10-29 20:22:15.954203');
INSERT INTO motorista (id, nome, cpf_hash, cpf_mascarado, pin_hash, cnh_categoria, operadora_id, ativo, criado_em) VALUES (3, 'João Pereira (demo)', '681bde2d397202c7be802136a5da6fac39bffa3c57aae0e7b684cab42e604671', '***.***.***-37', 'f71369ddf79af1bad2d235fd1f33fe073fcc00a486d3538b9f6bd0816f158e26', 'D', 2, TRUE, '2026-10-29 20:22:15.954206');
INSERT INTO motorista (id, nome, cpf_hash, cpf_mascarado, pin_hash, cnh_categoria, operadora_id, ativo, criado_em) VALUES (4, 'Rita Lima (demo)', 'dfde1f264827e294f267657808cf99958edad998f2b93fde66bef52653693bcc', '***.***.***-18', 'acf0ef49f0ad2bacb97a7ad7121857231477c45d9c54cdb454642b9ebbbdf907', 'D', 2, TRUE, '2026-10-29 20:22:15.954208');
SELECT setval(pg_get_serial_sequence('motorista', 'id'), (SELECT MAX(id) FROM motorista));

-- veiculo: 4 registro(s)
INSERT INTO veiculo (id, placa, modelo, tipo, capacidade, acessivel, ativo, operadora_id, motorista_id) VALUES (1, 'SVS1A23', '110-MASTER', 'VAN', 15, TRUE, TRUE, 1, 1);
INSERT INTO veiculo (id, placa, modelo, tipo, capacidade, acessivel, ativo, operadora_id, motorista_id) VALUES (2, 'SVS2B34', '109-MASTER', 'VAN', 12, FALSE, TRUE, 1, 2);
INSERT INTO veiculo (id, placa, modelo, tipo, capacidade, acessivel, ativo, operadora_id, motorista_id) VALUES (3, 'DEM0C56', 'Micro-ônibus urbano', 'MICROONIBUS', 26, TRUE, TRUE, 2, 3);
INSERT INTO veiculo (id, placa, modelo, tipo, capacidade, acessivel, ativo, operadora_id, motorista_id) VALUES (4, 'TST9D87', 'Van executiva', 'VAN', 10, FALSE, TRUE, 2, 4);
SELECT setval(pg_get_serial_sequence('veiculo', 'id'), (SELECT MAX(id) FROM veiculo));

-- paciente: 3 registro(s)
INSERT INTO paciente (id, nome, cpf_hash, cpf_mascarado, data_nascimento, telefone_mascarado, municipio_id, consentimento_em, ativo) VALUES (1, 'Paciente Demonstração Alfa', '47a9fc6b0d1cac3c2e80d92435aabf7d48e3e64670184991ab6fa4208374fff4', '***.***.***-38', '1990-05-12', '(13) ****-0001', 1, '2026-09-29 20:22:15.942985', TRUE);
INSERT INTO paciente (id, nome, cpf_hash, cpf_mascarado, data_nascimento, telefone_mascarado, municipio_id, consentimento_em, ativo) VALUES (2, 'Paciente Demonstração Beta', '01746c747e8cff51f894d95d08a2cc24af8089590c42608ea0776c2c936975cf', '***.***.***-19', '1985-11-03', '(13) ****-0002', 2, '2026-10-09 20:22:15.942985', TRUE);
INSERT INTO paciente (id, nome, cpf_hash, cpf_mascarado, data_nascimento, telefone_mascarado, municipio_id, consentimento_em, ativo) VALUES (3, 'Paciente Demonstração Gama', '40911cf5c7a370793cb9d1dd60b010731bd1cb0ccb7cf92c35a3179076adc229', '***.***.***-08', '1978-02-20', '(13) ****-0003', 1, '2026-10-19 20:22:15.942985', TRUE);
SELECT setval(pg_get_serial_sequence('paciente', 'id'), (SELECT MAX(id) FROM paciente));

-- unidade_saude: 5 registro(s)
INSERT INTO unidade_saude (id, nome, tipo, municipio_id, latitude, longitude) VALUES (1, 'UBS Nossa Senhora das Neves (demo)', 'UBS', 1, -23.938, -46.36);
INSERT INTO unidade_saude (id, nome, tipo, municipio_id, latitude, longitude) VALUES (2, 'UPA Central de Santos (demo)', 'UPA', 1, -23.953, -46.332);
INSERT INTO unidade_saude (id, nome, tipo, municipio_id, latitude, longitude) VALUES (3, 'Hospital Estadual de Referência — Diadema (demo)', 'HOSPITAL', 5, -23.686, -46.62);
INSERT INTO unidade_saude (id, nome, tipo, municipio_id, latitude, longitude) VALUES (4, 'Hospital das Clínicas — São Paulo (demo)', 'HOSPITAL', 4, -23.557, -46.67);
INSERT INTO unidade_saude (id, nome, tipo, municipio_id, latitude, longitude) VALUES (5, 'CER Baixada Santista (demo)', 'CER', 1, -23.965, -46.34);
SELECT setval(pg_get_serial_sequence('unidade_saude', 'id'), (SELECT MAX(id) FROM unidade_saude));

-- viagem: 4 registro(s)
INSERT INTO viagem (id, data, veiculo_id, motorista_id, origem_municipio_id, destino_unidade_id, destino_texto, trajeto, status, partida_prevista, retorno_previsto, iniciada_em, concluida_em, observacao) VALUES (1, '2026-10-29', 1, 1, 1, 3, 'Hospital Estadual de Referência — Diadema (demo)', 'IDA_E_VOLTA', 'EM_ANDAMENTO', '2026-10-29 06:00:00', '2026-10-29 18:00:00', '2026-10-29 06:05:00', NULL, NULL);
INSERT INTO viagem (id, data, veiculo_id, motorista_id, origem_municipio_id, destino_unidade_id, destino_texto, trajeto, status, partida_prevista, retorno_previsto, iniciada_em, concluida_em, observacao) VALUES (2, '2026-10-29', 2, 2, 2, 4, 'Hospital das Clínicas — São Paulo (demo)', 'IDA_E_VOLTA', 'PLANEJADA', '2026-10-29 07:30:00', '2026-10-29 19:00:00', NULL, NULL, NULL);
INSERT INTO viagem (id, data, veiculo_id, motorista_id, origem_municipio_id, destino_unidade_id, destino_texto, trajeto, status, partida_prevista, retorno_previsto, iniciada_em, concluida_em, observacao) VALUES (3, '2026-10-28', 1, 1, 1, 3, 'Hospital Estadual de Referência — Diadema (demo)', 'IDA_E_VOLTA', 'CONCLUIDA', '2026-10-28 06:00:00', '2026-10-28 18:00:00', '2026-10-28 06:12:00', '2026-10-28 17:40:00', NULL);
INSERT INTO viagem (id, data, veiculo_id, motorista_id, origem_municipio_id, destino_unidade_id, destino_texto, trajeto, status, partida_prevista, retorno_previsto, iniciada_em, concluida_em, observacao) VALUES (4, '2026-09-29', 2, 2, 2, 4, 'Hospital das Clínicas — São Paulo (demo)', 'IDA_E_VOLTA', 'CONCLUIDA', '2026-09-29 07:00:00', '2026-09-29 18:00:00', '2026-09-29 07:00:00', '2026-09-29 18:10:00', NULL);
SELECT setval(pg_get_serial_sequence('viagem', 'id'), (SELECT MAX(id) FROM viagem));

-- autorizacao: 6 registro(s)
INSERT INTO autorizacao (id, viagem_id, paciente_id, numero, status, origem, emitida_em, validada_em, validada_por) VALUES (1, 1, 1, 'AUT-20261029-001', 'APROVADA', 'SISTEMA', '2026-10-29 20:22:15.968969', '2026-10-27 20:22:15.942985', 'Central de Regulação (demo)');
INSERT INTO autorizacao (id, viagem_id, paciente_id, numero, status, origem, emitida_em, validada_em, validada_por) VALUES (2, 1, 2, 'AUT-20261029-002', 'APROVADA', 'OFICIO', '2026-10-29 20:22:15.968977', '2026-10-27 20:22:15.942985', 'Central de Regulação (demo)');
INSERT INTO autorizacao (id, viagem_id, paciente_id, numero, status, origem, emitida_em, validada_em, validada_por) VALUES (3, 1, 3, 'AUT-20261029-003', 'PENDENTE', 'SMS', '2026-10-29 20:22:15.968978', NULL, NULL);
INSERT INTO autorizacao (id, viagem_id, paciente_id, numero, status, origem, emitida_em, validada_em, validada_por) VALUES (4, 2, 3, 'AUT-20261029-004', 'APROVADA', 'SISTEMA', '2026-10-29 20:22:15.968979', '2026-10-28 20:22:15.942985', 'Central de Regulação (demo)');
INSERT INTO autorizacao (id, viagem_id, paciente_id, numero, status, origem, emitida_em, validada_em, validada_por) VALUES (5, 3, 1, 'AUT-20261028-001', 'APROVADA', 'SISTEMA', '2026-10-29 20:22:15.968980', NULL, NULL);
INSERT INTO autorizacao (id, viagem_id, paciente_id, numero, status, origem, emitida_em, validada_em, validada_por) VALUES (6, 4, 2, 'AUT-20260929-001', 'APROVADA', 'SISTEMA', '2026-10-29 20:22:15.968982', NULL, NULL);
SELECT setval(pg_get_serial_sequence('autorizacao', 'id'), (SELECT MAX(id) FROM autorizacao));

-- embarque: 1 registro(s)
INSERT INTO embarque (id, autorizacao_id, embarcado_em, desembarcado_em, metodo, registrado_por) VALUES (1, 1, '2026-10-29 06:12:00', NULL, 'QRCODE', 'Carlos Andrade (demo)');
SELECT setval(pg_get_serial_sequence('embarque', 'id'), (SELECT MAX(id) FROM embarque));

-- posicao: 27 registro(s)
INSERT INTO posicao (id, veiculo_id, viagem_id, latitude, longitude, velocidade_kmh, rumo, precisao_m, fonte, capturada_em, recebida_em) VALUES (1, 1, 1, -23.899437070938216, -46.4167914187643, 42.0, 310.0, 12.0, 'GATEWAY', '2026-10-29 19:10:15.942985', '2026-10-29 19:10:15.942985');
INSERT INTO posicao (id, veiculo_id, viagem_id, latitude, longitude, velocidade_kmh, rumo, precisao_m, fonte, capturada_em, recebida_em) VALUES (2, 1, 1, -23.89690308924485, -46.421479284897025, 46.0, 310.0, 12.0, 'GATEWAY', '2026-10-29 19:13:15.942985', '2026-10-29 19:13:15.942985');
INSERT INTO posicao (id, veiculo_id, viagem_id, latitude, longitude, velocidade_kmh, rumo, precisao_m, fonte, capturada_em, recebida_em) VALUES (3, 1, 1, -23.89414287617694, -46.42597957008349, 50.0, 310.0, 12.0, 'GATEWAY', '2026-10-29 19:16:15.942985', '2026-10-29 19:16:15.942985');
INSERT INTO posicao (id, veiculo_id, viagem_id, latitude, longitude, velocidade_kmh, rumo, precisao_m, fonte, capturada_em, recebida_em) VALUES (4, 1, 1, -23.890700235388167, -46.429914016699236, 54.0, 310.0, 12.0, 'GATEWAY', '2026-10-29 19:19:15.942985', '2026-10-29 19:19:15.942985');
INSERT INTO posicao (id, veiculo_id, viagem_id, latitude, longitude, velocidade_kmh, rumo, precisao_m, fonte, capturada_em, recebida_em) VALUES (5, 1, 1, -23.887257594599397, -46.43384846331497, 58.0, 310.0, 12.0, 'GATEWAY', '2026-10-29 19:22:15.942985', '2026-10-29 19:22:15.942985');
INSERT INTO posicao (id, veiculo_id, viagem_id, latitude, longitude, velocidade_kmh, rumo, precisao_m, fonte, capturada_em, recebida_em) VALUES (6, 1, 1, -23.883814953810624, -46.43778290993072, 42.0, 310.0, 12.0, 'GATEWAY', '2026-10-29 19:25:15.942985', '2026-10-29 19:25:15.942985');
INSERT INTO posicao (id, veiculo_id, viagem_id, latitude, longitude, velocidade_kmh, rumo, precisao_m, fonte, capturada_em, recebida_em) VALUES (7, 1, 1, -23.88037231302185, -46.441717356546455, 46.0, 310.0, 12.0, 'GATEWAY', '2026-10-29 19:28:15.942985', '2026-10-29 19:28:15.942985');
INSERT INTO posicao (id, veiculo_id, viagem_id, latitude, longitude, velocidade_kmh, rumo, precisao_m, fonte, capturada_em, recebida_em) VALUES (8, 1, 1, -23.87692967223308, -46.4456518031622, 50.0, 310.0, 12.0, 'GATEWAY', '2026-10-29 19:31:15.942985', '2026-10-29 19:31:15.942985');
INSERT INTO posicao (id, veiculo_id, viagem_id, latitude, longitude, velocidade_kmh, rumo, precisao_m, fonte, capturada_em, recebida_em) VALUES (9, 1, 1, -23.873487031444306, -46.44958624977794, 54.0, 310.0, 12.0, 'GATEWAY', '2026-10-29 19:34:15.942985', '2026-10-29 19:34:15.942985');
INSERT INTO posicao (id, veiculo_id, viagem_id, latitude, longitude, velocidade_kmh, rumo, precisao_m, fonte, capturada_em, recebida_em) VALUES (10, 1, 1, -23.870044390655533, -46.453520696393674, 58.0, 310.0, 12.0, 'GATEWAY', '2026-10-29 19:37:15.942985', '2026-10-29 19:37:15.942985');
INSERT INTO posicao (id, veiculo_id, viagem_id, latitude, longitude, velocidade_kmh, rumo, precisao_m, fonte, capturada_em, recebida_em) VALUES (11, 1, 1, -23.86660174986676, -46.45745514300942, 42.0, 310.0, 12.0, 'GATEWAY', '2026-10-29 19:40:15.942985', '2026-10-29 19:40:15.942985');
INSERT INTO posicao (id, veiculo_id, viagem_id, latitude, longitude, velocidade_kmh, rumo, precisao_m, fonte, capturada_em, recebida_em) VALUES (12, 1, 1, -23.863159109077987, -46.461389589625156, 46.0, 310.0, 12.0, 'GATEWAY', '2026-10-29 19:43:15.942985', '2026-10-29 19:43:15.942985');
INSERT INTO posicao (id, veiculo_id, viagem_id, latitude, longitude, velocidade_kmh, rumo, precisao_m, fonte, capturada_em, recebida_em) VALUES (13, 1, 1, -23.85964752260957, -46.46522911030378, 50.0, 310.0, 12.0, 'GATEWAY', '2026-10-29 19:46:15.942985', '2026-10-29 19:46:15.942985');
INSERT INTO posicao (id, veiculo_id, viagem_id, latitude, longitude, velocidade_kmh, rumo, precisao_m, fonte, capturada_em, recebida_em) VALUES (14, 1, 1, -23.855367743680915, -46.46801096660741, 54.0, 310.0, 12.0, 'GATEWAY', '2026-10-29 19:49:15.942985', '2026-10-29 19:49:15.942985');
INSERT INTO posicao (id, veiculo_id, viagem_id, latitude, longitude, velocidade_kmh, rumo, precisao_m, fonte, capturada_em, recebida_em) VALUES (15, 1, 1, -23.85108796475226, -46.47079282291104, 58.0, 310.0, 12.0, 'GATEWAY', '2026-10-29 19:52:15.942985', '2026-10-29 19:52:15.942985');
INSERT INTO posicao (id, veiculo_id, viagem_id, latitude, longitude, velocidade_kmh, rumo, precisao_m, fonte, capturada_em, recebida_em) VALUES (16, 1, 1, -23.846808185823605, -46.47357467921466, 42.0, 310.0, 12.0, 'GATEWAY', '2026-10-29 19:55:15.942985', '2026-10-29 19:55:15.942985');
INSERT INTO posicao (id, veiculo_id, viagem_id, latitude, longitude, velocidade_kmh, rumo, precisao_m, fonte, capturada_em, recebida_em) VALUES (17, 1, 1, -23.842528406894953, -46.476356535518285, 46.0, 310.0, 12.0, 'GATEWAY', '2026-10-29 19:58:15.942985', '2026-10-29 19:58:15.942985');
INSERT INTO posicao (id, veiculo_id, viagem_id, latitude, longitude, velocidade_kmh, rumo, precisao_m, fonte, capturada_em, recebida_em) VALUES (18, 1, 1, -23.838248627966298, -46.47913839182191, 50.0, 310.0, 12.0, 'GATEWAY', '2026-10-29 20:01:15.942985', '2026-10-29 20:01:15.942985');
INSERT INTO posicao (id, veiculo_id, viagem_id, latitude, longitude, velocidade_kmh, rumo, precisao_m, fonte, capturada_em, recebida_em) VALUES (19, 1, 1, -23.833968849037642, -46.48192024812553, 54.0, 310.0, 12.0, 'GATEWAY', '2026-10-29 20:04:15.942985', '2026-10-29 20:04:15.942985');
INSERT INTO posicao (id, veiculo_id, viagem_id, latitude, longitude, velocidade_kmh, rumo, precisao_m, fonte, capturada_em, recebida_em) VALUES (20, 1, 1, -23.82968907010899, -46.48470210442916, 58.0, 310.0, 12.0, 'GATEWAY', '2026-10-29 20:07:15.942985', '2026-10-29 20:07:15.942985');
INSERT INTO posicao (id, veiculo_id, viagem_id, latitude, longitude, velocidade_kmh, rumo, precisao_m, fonte, capturada_em, recebida_em) VALUES (21, 1, 1, -23.825409291180335, -46.48748396073278, 42.0, 310.0, 12.0, 'GATEWAY', '2026-10-29 20:10:15.942985', '2026-10-29 20:10:15.942985');
INSERT INTO posicao (id, veiculo_id, viagem_id, latitude, longitude, velocidade_kmh, rumo, precisao_m, fonte, capturada_em, recebida_em) VALUES (22, 1, 1, -23.82112951225168, -46.49026581703641, 46.0, 310.0, 12.0, 'GATEWAY', '2026-10-29 20:13:15.942985', '2026-10-29 20:13:15.942985');
INSERT INTO posicao (id, veiculo_id, viagem_id, latitude, longitude, velocidade_kmh, rumo, precisao_m, fonte, capturada_em, recebida_em) VALUES (23, 1, 1, -23.81684973332303, -46.49304767334004, 50.0, 310.0, 12.0, 'GATEWAY', '2026-10-29 20:16:15.942985', '2026-10-29 20:16:15.942985');
INSERT INTO posicao (id, veiculo_id, viagem_id, latitude, longitude, velocidade_kmh, rumo, precisao_m, fonte, capturada_em, recebida_em) VALUES (24, 1, 1, -23.812569954394373, -46.49582952964366, 54.0, 310.0, 12.0, 'GATEWAY', '2026-10-29 20:19:15.942985', '2026-10-29 20:19:15.942985');
INSERT INTO posicao (id, veiculo_id, viagem_id, latitude, longitude, velocidade_kmh, rumo, precisao_m, fonte, capturada_em, recebida_em) VALUES (25, 1, 1, -23.808290175465718, -46.498611385947285, 58.0, 310.0, 12.0, 'GATEWAY', '2026-10-29 20:22:15.942985', '2026-10-29 20:22:15.942985');
INSERT INTO posicao (id, veiculo_id, viagem_id, latitude, longitude, velocidade_kmh, rumo, precisao_m, fonte, capturada_em, recebida_em) VALUES (26, 2, NULL, -23.903250251716248, -46.40973703432494, 38.0, 300.0, 18.0, 'GATEWAY', '2026-10-29 20:20:45.942985', '2026-10-29 20:20:47.942985');
INSERT INTO posicao (id, veiculo_id, viagem_id, latitude, longitude, velocidade_kmh, rumo, precisao_m, fonte, capturada_em, recebida_em) VALUES (27, 3, NULL, -23.930691223220457, -46.3611007601935, 0.0, NULL, 35.0, 'GATEWAY', '2026-10-26 20:22:15.942985', '2026-10-26 20:22:15.942985');
SELECT setval(pg_get_serial_sequence('posicao', 'id'), (SELECT MAX(id) FROM posicao));

COMMIT;
