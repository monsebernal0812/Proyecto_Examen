DROP TABLE IF EXISTS creditos;

CREATE TABLE creditos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cliente TEXT NOT NULL,
  monto REAL NOT NULL CHECK (monto >= 0),
  tasa_interes REAL NOT NULL CHECK (tasa_interes >= 0),
  plazo INTEGER NOT NULL CHECK (plazo > 0),
  fecha_otorgamiento TEXT NOT NULL -- formato YYYY-MM-DD
);
