
import numpy as np
import matplotlib.pyplot as plt

class InterferenciaJensen:
    def __init__(self, k, power_curve, wind_speeds):
        self.k = k  # Constante de decaimento (offshore: 0.05, onshore: 0.075)
        self.power_curve = power_curve  # Curva de potência
        self.wind_speeds = wind_speeds  # Velocidade do vento correspondente à curva de potência

    def calcular_delta_V(self, U, C_t, D, X):
        # Usa a equação fornecida para calcular a redução de velocidade delta V
        delta_V = U * (1 - np.sqrt(1 - C_t)) * (D / (D + 2 * self.k * X))**2
        return delta_V

    def calcular_wake(self, X, Y, x_turbine, y_turbine, U, C_t, D):
        # Calcula a redução de velocidade delta V em uma grade de pontos X e Y
        dist_x = X - x_turbine
        dist_y = Y - y_turbine
        wake_width = D + 2 * self.k * dist_x
        in_wake = (dist_x > 0) & (np.abs(dist_y) <= wake_width / 2)

        # Aplica a equação de Jensen para calcular a redução de velocidade
        delta_V = self.calcular_delta_V(U, C_t, D, dist_x[in_wake])
        U_wake = U - delta_V  # Velocidade na região da esteira
        return U_wake, in_wake

    def aplicar_wake(self, X, Y, positions, U, C_t, D):
        # Inicializa o campo de vento com a velocidade do vento livre
        U_field = U * np.ones_like(X)

        # Aplica o efeito da esteira de cada turbina
        for pos in positions:
            U_wake, in_wake = self.calcular_wake(X, Y, pos[0], pos[1], U, C_t, D)
            U_field[in_wake] = np.minimum(U_field[in_wake], U_wake)

        return U_field

    def calcular_perda_potencia(self, U_turbina):
        # Interpola a curva de potência para obter a potência na nova velocidade do vento
        potencia = np.interp(U_turbina, self.wind_speeds, self.power_curve)
        return potencia

    def plotar_efeito_esteira(self, X, Y, U_field, positions, D):
        # Plota o campo de vento com as esteiras
        plt.figure(figsize=(10, 7.68))
        plt.contourf(X, Y, U_field, levels=np.linspace(0, U_field.max(), 256), cmap='Blues_r')
        plt.colorbar(label='Velocidade do Vento (m/s)')
        plt.axis('equal')

        # Adiciona círculos com borda vermelha e interior branco para representar as turbinas
        for pos in positions:
            turbine_circle = plt.Circle((pos[0], pos[1]), D / 2, edgecolor='red', facecolor='white', linewidth=2)
            plt.gca().add_patch(turbine_circle)

        plt.title('Efeito Esteira')
        plt.xlabel('Eixo X (m)')
        plt.ylabel('Eixo Y (m)')
        plt.grid(True)
        plt.show()
