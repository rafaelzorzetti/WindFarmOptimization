
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.interpolate import RegularGridInterpolator

class InterferenciaJensen:
    def __init__(self, k, power_curve, wind_speeds):
        self.k = k  # Constante de decaimento (offshore: 0.05, onshore: 0.075)
        self.power_curve = power_curve  # Curva de potência
        self.wind_speeds = wind_speeds  # Velocidade do vento correspondente à curva de potência

    def calcular_delta_V(self, U, C_t, D, X):
        # Usa a equação fornecida para calcular a redução de velocidade delta V
        delta_V = U * (1 - np.sqrt(1 - C_t)) * (D / (D + 2 * self.k * X))**2
        return delta_V

    def calcular_wake(self, X, Y, x_turbina, y_turbina, U, C_t, D, wd):
        # Converte a direção do vento de graus para radianos e ajusta para a convenção matemática
        theta = np.radians(270 - wd)

        # Calcula as distâncias relativas à turbina
        delta_x = X - x_turbina
        delta_y = Y - y_turbina

        # Rotaciona as coordenadas para alinhar com a direção do vento
        dist_x = delta_x * np.cos(theta) + delta_y * np.sin(theta)
        dist_y = -delta_x * np.sin(theta) + delta_y * np.cos(theta)

        # Calcula a largura da esteira
        wake_width = D + 2 * self.k * dist_x

        # Determina os pontos que estão dentro da esteira
        in_wake = (dist_x > 0) & (np.abs(dist_y) <= wake_width / 2)

        # Aplica a equação de Jensen para calcular a redução de velocidade
        delta_V = self.calcular_delta_V(U, C_t, D, dist_x[in_wake])
        U_wake = U - delta_V  # Velocidade na região da esteira
        return U_wake, in_wake

    def aplicar_wake(self, X, Y, positions, wind_scenarios, C_t, D):
        # Inicializa o campo de vento com zeros
        U_field = np.zeros_like(X)

        # Loop sobre os cenários de vento
        for scenario in wind_scenarios:
            U = scenario['U']
            wd = scenario['wd']
            prob = scenario['prob']

            # Inicializa o campo de vento para este cenário
            U_scenario = U * np.ones_like(X)

            # Aplica o efeito da esteira de cada turbina
            for pos in positions:
                U_wake, in_wake = self.calcular_wake(X, Y, pos[0], pos[1], U, C_t, D, wd)
                U_scenario[in_wake] = np.minimum(U_scenario[in_wake], U_wake)

            # Acumula o campo de vento ponderado pela probabilidade
            U_field += prob * U_scenario

        return U_field

    def calcular_perda_potencia(self, U_turbina):
        # Interpola a curva de potência para obter a potência na nova velocidade do vento
        potencia = np.interp(U_turbina, self.wind_speeds, self.power_curve)
        return potencia
    
    def calcular_wi(self, positions, U_field, X, Y):
        wi = {}

        # Criar interpolador para o campo de vento
        interpolador = RegularGridInterpolator((Y[:, 0], X[0, :]), U_field)

        for i, (x, y) in enumerate(positions):
            # Interpola o valor de U_field na posição da turbina (x, y)
            U_i = interpolador([y, x])  # Nota: scipy usa (y, x) para coordenadas 2D

            # Calcula a potência máxima (sem interferência) e a potência com interferência
            U_max = np.max(U_field)
            potencia_maxima = np.interp(U_max, self.wind_speeds, self.power_curve)
            potencia_com_interferencia = np.interp(U_i, self.wind_speeds, self.power_curve)

            # A interferência máxima w_i é a diferença entre a potência máxima e a potência com interferência
            wi[i] = potencia_maxima - potencia_com_interferencia

        return wi   
    
    def plotar_efeito_esteira(self, X, Y, U_field, positions, D):
        # Cria um colormap personalizado
        colors = [
            (0.0, 'white'),         # Velocidade mínima (vermelho)
            (0.5, 'lightblue'),   # Velocidade média (azul claro)
            (1.0, 'darkblue')     # Velocidade máxima (azul escuro)
        ]
        custom_cmap = LinearSegmentedColormap.from_list('custom_cmap', colors)

        plt.figure(figsize=(10, 7))
        # Definir os limites dos eixos X e Y
        plt.xlim([0, 4000])  # Limite do eixo X (ajustado conforme necessário)
        plt.ylim([0, 4000])  # Limite ajustado do eixo Y para focar nas turbinas
        plt.contourf(X, Y, U_field, levels=np.linspace(5, U_field.max(), 256), cmap=custom_cmap)
        plt.colorbar(label='Velocidade do Vento (m/s)')
        plt.axis('equal')

        # Adiciona círculos para representar as turbinas em vermelho
        for pos in positions:
            turbine_circle = plt.Circle((pos[0], pos[1]), D / 2, edgecolor='red', facecolor='red', linewidth=2)
            plt.gca().add_patch(turbine_circle)
        
        # Defina os limites dos eixos X e Y para garantir que todo o parque eólico seja visualizado
        plt.title('Efeito Esteira')
        plt.xlabel('Eixo X (m)')
        plt.ylabel('Eixo Y (m)')
        plt.grid(False)
        plt.show()
    
     