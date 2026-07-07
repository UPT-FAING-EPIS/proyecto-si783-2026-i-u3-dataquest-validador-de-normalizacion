CREATE TABLE ventas (
    factura_id INT,
    producto_id INT,
    cliente_nombre_completo VARCHAR(100),
    cliente_direccion VARCHAR(200),
    producto_nombre VARCHAR(100),
    producto_categoria VARCHAR(50),
    cantidad INT,
    precio_unitario DECIMAL(10,2),
    colores_disponibles VARCHAR(100),
    PRIMARY KEY (factura_id, producto_id)
);
