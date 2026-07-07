import matplotlib.pyplot as plt

def render_schema(esquema):
    """
    Genera un schema visual de las tablas con matplotlib.
    Retorna la figura.
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    
    # Placeholder
    ax.text(0.5, 0.5, 'Schema de Tablas\n(Placeholder visual)', 
            horizontalalignment='center', verticalalignment='center', fontsize=12)
    ax.axis('off')
    
    return fig
