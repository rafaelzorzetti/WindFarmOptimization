import gurobipy as gp
from gurobipy import GRB
import numpy as np

class WindFarmOptimization:
    def __init__(self, positions, D_min, num_turbinas, interferencia_jensen, wind_scenarios, C_t, D, power_curve, wind_speeds):
        self.positions = positions
        self.D_min = D_min
        self.num_turbinas = num_turbinas
        self.interferencia_jensen = interferencia_jensen
        self.wind_scenarios = wind_scenarios
        self.C_t = C_t
        self.D = D
        self.power_curve = power_curve
        self.wind_speeds = wind_speeds
        self.model = gp.Model("WindFarmOptimization")
        self.model.Params.OutputFlag = 1  # Ativa o log do Gurobi

    def dist(self, i, j):
        """Calcula a distância entre duas posições candidatas i e j."""
        xi, yi = self.positions[i]
        xj, yj = self.positions[j]
        return np.sqrt((xi - xj)**2 + (yi - yj)**2)

    def _build_model(self, U_field, X, Y):
        # Variáveis de decisão: x[i] = 1 se houver uma turbina na posição candidata i
        x = self.model.addVars(len(self.positions), vtype=GRB.BINARY, name="x")

        # Calcula os valores de w_i para cada posição candidata
        wi = self.interferencia_jensen.calcular_wi(self.positions, U_field, X, Y)

        # Imprimir todos os valores de wi e garantir que sejam escalares
        print("Valores de wi:")
        for i in range(len(self.positions)):
            if isinstance(wi[i], np.ndarray):
                wi[i] = wi[i].item()  # Converte para valor escalar se for um array
            print(f"wi[{i}] = {wi[i]}")  # Imprime cada valor de wi

            # Verifique se wi[i] é numérico
            if not isinstance(wi[i], (int, float)):
                raise ValueError(f"Erro: wi[{i}] não é um valor numérico.")

        # Função objetivo: Maximizar a produção de energia líquida
        self.model.setObjective(
            gp.quicksum((1 - wi[i]) * x[i] for i in range(len(self.positions))),
            GRB.MAXIMIZE
        )

        # Restrição: Exatamente 'num_turbinas' turbinas no layout
        self.model.addConstr(gp.quicksum(x[i] for i in range(len(self.positions))) == self.num_turbinas)

        # Restrição: Distância mínima entre as turbinas
        for i in range(len(self.positions)):
            for j in range(i + 1, len(self.positions)):
                if self.dist(i, j) < self.D_min:
                    self.model.addConstr(x[i] + x[j] <= 1, name=f"DistMin_{i}_{j}")

        self.x = x


    def solve(self, U_field, X, Y):
        """Constroi e resolve o modelo de otimização"""
        self._build_model(U_field, X, Y)
        self.model.optimize()

        # Verificar e exibir status do modelo
        if self.model.Status == GRB.OPTIMAL:
            layout = [self.positions[i] for i in range(len(self.positions)) if self.x[i].x > 0.5]
            total_energy = self.model.ObjVal
            print("Layout ótimo encontrado com energia total:", total_energy)
            return layout, total_energy
        elif self.model.Status == GRB.TIME_LIMIT:
            print("A solução atingiu o limite de tempo.")
        elif self.model.Status == GRB.INFEASIBLE:
            print("O modelo é inviável.")
        else:
            print(f"Status do modelo: {self.model.Status}")
        return None, None

