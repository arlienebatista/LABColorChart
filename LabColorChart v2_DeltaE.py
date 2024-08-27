import numpy as np
import FreeSimpleGUI as sg
import os
import colorsys
import matplotlib.pyplot as plt
import tempfile
import atexit

# Função para calcular o delta E
def calculate_delta_e(lab1, lab2):
    delta_e = np.sqrt(sum((x1 - x2) ** 2 for x1, x2 in zip(lab1, lab2)))
    return delta_e

# Função para criar a janela de cálculo do Delta E
def delta_e_window():
    layout = [
        [sg.Text('Insira os valores de referencia de L*a*b*:')],
        [sg.Text('L1:', size=(2, 1)), sg.InputText(key='L1')],
        [sg.Text('a1:', size=(2, 1)), sg.InputText(key='a1')],
        [sg.Text('b1:', size=(2, 1)), sg.InputText(key='b1')],
        [sg.Text('')],
        [sg.Text('Insira os valores de L*a*b* da amostra:')],
        [sg.Text('L2:', size=(2, 1)), sg.InputText(key='L2')],
        [sg.Text('a2:', size=(2, 1)), sg.InputText(key='a2')],
        [sg.Text('b2:', size=(2, 1)), sg.InputText(key='b2')],
        [sg.Text('')],
        [sg.Text('Delta E:', size=(10, 1)), sg.Text('', key='delta_e')],
        [sg.Text('')],
        [sg.Button('Calcular', size=(10, 1)), sg.Button('Fechar', size=(10, 1))]
    ]

    window = sg.Window('Calcular Delta E', layout, size=(400, 380), element_justification='center')

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == 'Fechar':
            break

        if event == 'Calcular':
            try:
                L1 = float(values['L1'])
                a1 = float(values['a1'])
                b1 = float(values['b1'])
                L2 = float(values['L2'])
                a2 = float(values['a2'])
                b2 = float(values['b2'])

                lab1 = [L1, a1, b1]
                lab2 = [L2, a2, b2]
                
                delta_e = calculate_delta_e(lab1, lab2)
                window['delta_e'].update(f'{delta_e:.2f}')

            except ValueError:
                sg.popup_ok('Por favor, insira valores válidos para L*a*b*.')

    window.close()


# Função para gerar a roda de cores
def generate_color_wheel():
    num_points = 360
    hues = np.linspace(0, 1, num_points)
    saturations = np.linspace(0, 1, num_points)
    lightness = 0.5  # Luminosidade em 50%

    hsl_values = np.array([[hue, saturation, lightness]
                          for hue in hues for saturation in saturations])

    rgb_values = np.array([colorsys.hls_to_rgb(h, l, s)
                          for h, s, l in hsl_values])

    hues = hsl_values[:, 0].reshape((num_points, num_points))
    saturations = hsl_values[:, 1].reshape((num_points, num_points))
    rgb_values = rgb_values.reshape((num_points, num_points, 3))

    fig, ax = plt.subplots(subplot_kw=dict(projection='polar'))
    ax.set_theta_direction(1)
    ax.set_theta_offset(np.pi / 6.0)
    ax.set_position([0, 0, 1, 1])
    ax.set_rlabel_position(1)

    r_ticks = np.linspace(0, 1, 6)
    r_labels = [f'{int(t*100)}' for t in r_ticks]
    ax.set_yticks(r_ticks)
    ax.set_yticklabels(r_labels, color='gray', fontsize=8)

    c = ax.pcolormesh(hues * 2 * np.pi, saturations, rgb_values)

    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid(False)

    def excluir_arquivo_temporario(file_path):
        os.unlink(file_path)

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
        image_path = temp_file.name

    image_path = 'color_wheel.png'
    plt.savefig(image_path, dpi=100, bbox_inches='tight', pad_inches=0)
    plt.close()

    atexit.register(excluir_arquivo_temporario, image_path)

    return image_path

# Função para criar o gráfico de cores LAB
def create_lab_color_chart(L_valores, a_valores, b_valores, imagem_path):
    try:
        imagem = plt.imread(imagem_path)

        fig, ax = plt.subplots()
        ax.imshow(imagem, extent=[-100, 100, -100, 100], alpha=1)

        scatter = ax.scatter(
            a_valores, b_valores,
            color=['none' if x >= 0 and y >= 0 else 'none' for x,
                   y in zip(a_valores, b_valores)],
            edgecolors='black', linewidths=1.5
        )

        for a, b in zip(a_valores, b_valores):
            ax.annotate(f'({a};{b})', (a, b), textcoords="offset points",
                        xytext=(0, 5), ha='center', va='bottom', fontsize=8)  # Tamanho da fonte ajustado)

        ax.set_ylabel('a*')
        ax.set_xlabel('b*')
        ax.set_title('CIELab')

        ax.axhline(0, color='black', linewidth=0.7, linestyle='--')
        ax.axvline(0, color='black', linewidth=0.5, linestyle='--')

        plt.grid(True, linestyle='--', alpha=0.6)
        ax.set_xlim(-100, 100)
        ax.set_ylim(-100, 100)

        cax = fig.add_axes([0.85, 0.1, 0.04, 0.79])
        cmap = plt.cm.gray
        norm = plt.Normalize(0, 100)
        cb = plt.colorbar(plt.cm.ScalarMappable(cmap=cmap, norm=norm), cax=cax)
        cb.set_label('L*')

        point = L_valores
        normalized_point = point
        cb.ax.plot([0, 1], [normalized_point, normalized_point],
                   color='red', linewidth=5, marker='_', markersize=8, label='Manual Point')

        plt.show()

    except Exception as e:
        sg.popup_error(f"Erro ao exibir o gráfico: {str(e)}")

# Função para mostrar as referências
def show_references():
    references = """TEIXEIRA, Renires et al. LAB Color Chart: Demonstra o ponto de cor no espaço CIELab. [programa de computador]. Versão 2.0. Local de publicação: Universidade Federal de Pelotas-UFPel, 2024
    """
    sg.popup_scrolled(references, title="Referências")

# Função principal
def main():
    sg.theme('DarkGrey11')

    layout = [
        [sg.Text('')],  
        [sg.Text('Informe os valores de L*a*b* para gerar o grafico de cores CIELab:', size=(30, 2), justification='center')],
        [sg.Text('')],  
        [sg.Text('L*:', size=(2, 1)), sg.InputText(key='L')],
        [sg.Text('a*:', size=(2, 1)), sg.InputText(key='a')],
        [sg.Text('b*:', size=(2, 1)), sg.InputText(key='b')],
        [sg.Text('')],  
        [sg.Button('Mostrar', size=(10, 1)), sg.Button('Limpar', size=(10, 1)), sg.Button('Sair', size=(10, 1))],
        [sg.Text('')],  
        [sg.Button('Calcular Delta E', size=(15, 1))], 
        [sg.Text('')], 
        [sg.Button ('Referências', size=(10, 1), key='Referências', pad=((0, 10), (5, 10)))],
        [sg.Text('2024 © LAB Color Chart v.2.0', size=(30, 1), font=('Arial Bold', 8), justification='center')],  
    ]
    

    window = sg.Window('LAB Color Chart', 
                       layout, 
                       size=(600, 400), # Tamanho da janela principal
                       element_justification='center')

    L_valores = []
    a_valores = []
    b_valores = []

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == 'Sair':
            break

        if event == 'Mostrar':
            try:
                L_valores.append(float(values['L']))
                a_valores.append(float(values['a']))
                b_valores.append(float(values['b']))

                imagem_path = generate_color_wheel()
                create_lab_color_chart(L_valores, a_valores, b_valores, imagem_path)

            except ValueError:
                sg.popup_ok('Por favor, insira valores válidos para L*a*b*.')

        if event == 'Limpar':
            window['L'].update('')
            window['a'].update('')
            window['b'].update('')
            L_valores.clear()
            a_valores.clear()
            b_valores.clear()

        if event == 'Calcular Delta E':
            delta_e_window()

        if event == 'Referências':
            show_references()

    window.close()

# Execução da função principal
if __name__ == "__main__":
    main()
