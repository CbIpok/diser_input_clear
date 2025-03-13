import matplotlib.pyplot as plt
import numpy as np
from calc_total_acc import TotalAccuracy
import plotly.graph_objects as go


class PlotTotalAccuracy(TotalAccuracy):
    def plot(self, x, y):
        """
        Строит 2D графики для конкретной точки (x, y) коэффициентной сетки:
          - Исходная волна (wave)
          - Реконструкция (reconstruction)
          - Разница (wave - reconstruction)

        Параметры:
          x - индекс строки коэффициентной сетки.
          y - индекс столбца коэффициентной сетки.
        """
        # Объединяем базисные функции в массив: shape (n_layers, H, W)
        basis_stack = np.stack(self.basis, axis=0)
        # Получаем коэффициенты для выбранной точки (x, y)
        coef = self.coefs[x, y, :]
        # Вычисляем реконструкцию для данной точки
        reconstruction = np.tensordot(coef, basis_stack, axes=([0], [0]))
        # Вычисляем разницу между волной и реконструкцией
        difference = self.wave - reconstruction

        # Построение графиков
        fig, axs = plt.subplots(1, 3, figsize=(18, 6))
        axs[0].imshow(self.wave, cmap="viridis")
        axs[0].set_title("Wave")
        axs[1].imshow(reconstruction, cmap="viridis")
        axs[1].set_title("Reconstruction")
        axs[2].imshow(difference, cmap="viridis")
        axs[2].set_title("Difference (Wave - Reconstruction)")

        for ax in axs:
            ax.axis("off")
        plt.tight_layout()
        plt.show()

    def plot3d(self, x, y):
        """
        Строит 3D поверхности для волны (wave) и реконструкции (reconstruction)
        для конкретной точки (x, y) коэффициентной сетки с помощью plotly.

        Параметры:
          x - индекс строки коэффициентной сетки.
          y - индекс столбца коэффициентной сетки.
        """
        # Объединяем базисные функции в массив: shape (n_layers, H, W)
        basis_stack = np.stack(self.basis, axis=0)
        # Получаем коэффициенты для выбранной точки (x, y)
        coef = self.coefs[x, y, :]
        # Вычисляем реконструкцию для данной точки
        reconstruction = np.tensordot(coef, basis_stack, axes=([0], [0]))

        # Создаём координатную сетку для осей X и Y, основываясь на размере волны
        H, W = self.wave.shape
        x_coords = np.arange(W)
        y_coords = np.arange(H)
        X, Y = np.meshgrid(x_coords, y_coords)

        # Создаём фигуру Plotly
        fig = go.Figure()

        # Добавляем поверхность исходной волны
        fig.add_trace(go.Surface(
            x=X, y=Y, z=self.wave,
            colorscale='Viridis',
            name='Wave',
            showscale=False
        ))

        # Добавляем поверхность реконструкции
        fig.add_trace(go.Surface(
            x=X, y=Y, z=reconstruction,
            colorscale='Cividis',
            opacity=0.7,
            name='Reconstruction',
            showscale=False
        ))

        fig.update_layout(
            title=f"3D Plot for Point ({x}, {y})",
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Amplitude'
            ),
            autosize=True
        )
        fig.show()

if __name__ == "__main__":
    basises = [
        "basis_6",
        "basis_8",
        "basis_9",
        "basis_10",
        "basis_12",
        "basis_15",
        "basis_16",
        "basis_18",
        "basis_20",
        "basis_24",
        "basis_25",
        "basis_30",
        "basis_36",
        "basis_40",
        "basis_48"
    ]

    bathes = [
        "parabola_200_2000",
        "parabola_sine_200_2000",
        "x_200_2000",
        "y_200_2000",
    ]
    waves = [
        "gaus_double_1_2",
        "gaus_double_2_1",
        "gaus_single_2"
    ]
    basis = "basis_48"
    bath = "parabola_sine_200_2000"
    calculator = PlotTotalAccuracy(r"E:\tsunami_res_dir\n_accurate_set", bath, basis,waves[0])
    calculator.plot3d(150,200)