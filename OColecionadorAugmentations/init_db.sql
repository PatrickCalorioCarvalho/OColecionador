CREATE TABLE IF NOT EXISTS imagens (
    id SERIAL PRIMARY KEY,
    item_id VARCHAR(100) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    original VARCHAR(255) NOT NULL,
    variacao VARCHAR(255) NOT NULL,
    dataset_split VARCHAR(10) NOT NULL,
    bucket VARCHAR(100) NOT NULL,
    caminho VARCHAR(255) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_item_id ON imagens(item_id);
CREATE INDEX idx_split_categoria ON imagens(dataset_split, categoria);
