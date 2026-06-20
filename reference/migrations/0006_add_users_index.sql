-- Applied migration. Immutable once shipped.
CREATE INDEX idx_users_email ON users(email);
