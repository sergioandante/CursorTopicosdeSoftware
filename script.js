document.addEventListener('DOMContentLoaded', () => {
    const deployBtn = document.getElementById('deployBtn');
    const toast = document.getElementById('toast');
    const bars = document.querySelectorAll('.bar');

    // Animación de entrada para las barras de la gráfica
    bars.forEach(bar => {
        const targetHeight = bar.style.height;
        bar.style.height = '0';
        setTimeout(() => {
            bar.style.height = targetHeight;
        }, 500);
    });

    // Simulación de despliegue
    deployBtn.addEventListener('click', () => {
        deployBtn.innerText = '⌛ Desplegando...';
        deployBtn.disabled = true;
        deployBtn.style.opacity = '0.7';

        setTimeout(() => {
            toast.classList.add('show');
            deployBtn.innerText = '🚀 Desplegado';
            deployBtn.style.background = '#22c55e';
            deployBtn.style.boxShadow = '0 0 20px rgba(34, 197, 94, 0.5)';

            setTimeout(() => {
                toast.classList.remove('show');
            }, 3000);
        }, 2000);
    });

    // Efecto de brillo al mover el ratón sobre las tarjetas
    const cards = document.querySelectorAll('.card, .stat-card');
    cards.forEach(card => {
        card.addEventListener('mousemove', e => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            card.style.setProperty('--mouse-x', `${x}px`);
            card.style.setProperty('--mouse-y', `${y}px`);
        });
    });
});
