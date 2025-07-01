CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    tipo VARCHAR(10) CHECK (tipo IN ('Morador', 'Sindico')) NOT NULL
);

CREATE TABLE Morador (
    usuarios_id INTEGER PRIMARY KEY REFERENCES usuarios(id),
    apartamento VARCHAR(10) NOT NULL
);

CREATE TABLE Sindico (
    usuarios_id INTEGER PRIMARY KEY REFERENCES usuarios(id)
);

ALTER TABLE Sindico ADD COLUMN created_at TIMESTAMP DEFAULT NOW();

ALTER TABLE Morador ADD COLUMN created_at TIMESTAMP DEFAULT NOW();

CREATE TABLE Ocorrencia (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(100) NOT NULL,
    descricao TEXT NOT NULL,
    status VARCHAR(30),
    data TIMESTAMP NOT NULL,
    fotos TEXT[],
    morador_id INTEGER NOT NULL REFERENCES Morador(usuarios_id)
);

CREATE TABLE Reserva (
    id SERIAL PRIMARY KEY,
    area VARCHAR(100),
    data_inicio TIMESTAMP NOT NULL,
    data_fim TIMESTAMP NOT NULL,
    status VARCHAR(30),
    morador_id INTEGER NOT NULL REFERENCES Morador(usuarios_id)
);

ALTER TABLE Reserva ADD COLUMN observacoes TEXT
ALTER TABLE Reserva ADD COLUMN horario varchar(30)
ALTER TABLE Reserva ADD COLUMN motivo TEXT

CREATE TABLE Comunicado (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(100) NOT NULL,
    mensagem TEXT NOT NULL,
    data_publicacao TIMESTAMP NOT NULL,
    arquivos TEXT[],  
    usuario_id INTEGER NOT NULL REFERENCES Sindico(usuarios_id)
);

CREATE TABLE Relatorio (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(100) NOT NULL,
    periodo VARCHAR(50),
    conteudo TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS NotificationReadStatus (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    notification_id INTEGER NOT NULL,
    read_status BOOLEAN NOT NULL DEFAULT FALSE,
    read_timestamp TIMESTAMP NULL,
    CONSTRAINT fk_user FOREIGN KEY(user_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    UNIQUE(user_id, notification_id)
);


ALTER TABLE NotificationReadStatus
    ADD COLUMN notification_type VARCHAR(20) NOT NULL DEFAULT 'reserva';

ALTER TABLE NotificationReadStatus
    DROP CONSTRAINT notificationreadstatus_user_id_notification_id_key,
    ADD    CONSTRAINT notificationreadstatus_user_notif_type_id_uk
           UNIQUE (user_id, notification_type, notification_id);


CREATE TABLE IF NOT EXISTS imagens ( 
id SERIAL PRIMARY KEY,
filename VARCHAR(255) NOT NULL,
data BYTEA NOT NULL
);


CREATE INDEX idx_notification_read_status_user_id ON NotificationReadStatus(user_id);
CREATE INDEX idx_notification_read_status_notification_type ON NotificationReadStatus(notification_type);
CREATE INDEX idx_notification_read_status_read_timestamp ON NotificationReadStatus(read_timestamp);

CREATE INDEX idx_reserva_morador_id ON Reserva(morador_id);
CREATE INDEX idx_reserva_status ON Reserva(status);
CREATE INDEX idx_reserva_data_inicio ON Reserva(data_inicio);

CREATE INDEX idx_ocorrencia_morador_id ON Ocorrencia(morador_id);
CREATE INDEX idx_ocorrencia_status ON Ocorrencia(status);
CREATE INDEX idx_ocorrencia_data ON Ocorrencia(data);



CREATE TABLE IF NOT EXISTS arquivos (
    id SERIAL PRIMARY KEY,
    nome_arquivo VARCHAR(255) NOT NULL,
    tipo_mime VARCHAR(100) NOT NULL,
    dados BYTEA NOT NULL,
    data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_id INTEGER REFERENCES usuarios(id)
);

ALTER TABLE Ocorrencia 
ADD COLUMN IF NOT EXISTS fotos_id INTEGER[];

ALTER TABLE Comunicado 
ADD COLUMN IF NOT EXISTS arquivos_id INTEGER[];

CREATE INDEX IF NOT EXISTS idx_arquivos_usuario_id ON arquivos(usuario_id);
CREATE INDEX IF NOT EXISTS idx_ocorrencia_fotos_id ON Ocorrencia USING GIN(fotos_id);
CREATE INDEX IF NOT EXISTS idx_comunicado_arquivos_id ON Comunicado USING GIN(arquivos_id);