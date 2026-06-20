-- Pending migration. Still immutable to the agent; humans own migration changes.
CREATE INDEX idx_orders_status ON orders(status);
