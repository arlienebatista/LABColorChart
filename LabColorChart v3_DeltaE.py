import numpy as np
import FreeSimpleGUI as sg
import os
import colorsys
import matplotlib.pyplot as plt
import tempfile
import atexit

# Lista de marcadores disponíveis no matplotlib
MARKERS = ['o', 's', 'X', 'v', 'p', '*', 'h', '>', '<', 'H', 'D', 'd', '^']

# Função para calcular o delta E
def calculate_delta_e(lab1, lab2):
    delta_e = np.sqrt(sum((x1 - x2) ** 2 for x1, x2 in zip(lab1, lab2)))
    return delta_e

# Função para criar a janela de cálculo do Delta E
def delta_e_window():
    layout = [
        [sg.Text('Insira os valores de L*a*b* da referência:')],
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
    ax.set_theta_direction(1)  # Direção do ângulo
    ax.set_theta_offset(np.pi / 6.0)  # Offset para o início em cima
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

    # Criar arquivo temporário e garantir que será fechado corretamente
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    temp_file.close()  # Fechar o arquivo para que o matplotlib possa escrever nele
    image_path = temp_file.name
    
    plt.savefig(image_path, dpi=100, bbox_inches='tight', pad_inches=0)
    plt.close()

    # Registrar função para excluir o arquivo apenas se ele existir
    def excluir_arquivo_temporario(file_path):
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception:
            pass  # Ignorar quaisquer erros durante a exclusão

    atexit.register(excluir_arquivo_temporario, image_path)

    return image_path

# Função para gerar o gráfico (modificada para incluir nomes na legenda)
def create_lab_color_chart(L_valores, a_valores, b_valores, imagem_path, sample_names=None):
    try:
        imagem = plt.imread(imagem_path)

        # Aumentar o tamanho da figura (largura, altura em polegadas)
        fig = plt.figure(figsize=(10, 9))
        
        # Ajustar os gridspecs para o novo tamanho
        gs = fig.add_gridspec(2, 1, height_ratios=[0.9, 0.15], hspace=0.4)  # Ajustado hspace e ratios
        gs_top = gs[0].subgridspec(1, 2, width_ratios=[0.9, 0.04], wspace=0.1)  # Ajustado wspace
        
        ax = fig.add_subplot(gs_top[0])  # Gráfico principal
        cax = fig.add_subplot(gs_top[1])  # Barra de cores
        legend_ax = fig.add_subplot(gs[1])  # Área para legenda
        
        ax.imshow(imagem, extent=[-128, 128, -128, 128], alpha=1)

        # Configuração aprimorada do grid
        ax.grid(True, which='both', linestyle=':', color='lightgray', linewidth=0.6, alpha=0.7)
        ax.set_axisbelow(True)
        ax.grid(True, which='major', linestyle='--', color='gray', linewidth=0.8, alpha=0.5)
        
        ax.set_xlim(-128, 128)
        ax.set_ylim(-128, 128)
    
        # Criar lista de marcadores para cada ponto
        markers = []
        scatter_plots = []
        for i in range(len(a_valores)):
            markers.append(MARKERS[i % len(MARKERS)])
            
            if sample_names and i < len(sample_names):
                label = f" {sample_names[i]} (L*:{L_valores[i]:.2f}, a*:{a_valores[i]:.2f}, b*:{b_valores[i]:.2f})"
            else:
                label = f" Amostra {i+1} (L*:{L_valores[i]:.2f}, a*:{a_valores[i]:.2f}, b*:{b_valores[i]:.2f})"
            
            scatter = ax.scatter(
                a_valores[i], b_valores[i],
                marker=markers[i],
                color='none',
                edgecolors='black',
                linewidths=1.0,
                s=80,
                label=label
            )
            scatter_plots.append(scatter)

        # Aumentar o tamanho da fonte dos eixos
        ax.set_ylabel('a*', fontsize=12)
        ax.set_xlabel('b*', fontsize=12)
        ax.set_title('CIELab', fontsize=14)

        ax.axhline(0, color='black', linewidth=0.7, linestyle='--')
        ax.axvline(0, color='black', linewidth=0.5, linestyle='--')

        # Barra de cores para L*
        cmap = plt.cm.gray
        norm = plt.Normalize(0, 100)
        cb = plt.colorbar(plt.cm.ScalarMappable(cmap=cmap, norm=norm), cax=cax)
        cb.set_label('L*', fontsize=12)
        
        for i, L in enumerate(L_valores):
            cax.plot([0, 1], [L, L], 
                    color='red',
                    linewidth=2,
                    transform=cax.get_yaxis_transform())

        # Legenda vertical
        legend_ax.axis('off')
        legend = legend_ax.legend(handles=scatter_plots, 
                                loc='upper left',
                                bbox_to_anchor=(0, 1.25), 
                                ncol=2,
                                fontsize=12,
                                markerscale=2.0,
                                frameon=False)
        
        # Substituir tight_layout por ajustes manuais
        plt.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9, hspace=0.4)
        plt.show()

    except Exception as e:
        sg.popup_error(f"Erro ao exibir o gráfico: {str(e)}")

# Função para mostrar as referências
def show_references():
    references = """TEIXEIRA, R.S. et al. LAB Color Chart: Demonstra o ponto de cor no espaço CIELab. [programa de computador]. Versão 3.0. Titular: Universidade Federal de Pelotas-UFPel, 2024
    """
    sg.popup_scrolled(references, title="Referências")

# Função principal
def main():
    sg.theme('DarkGrey11')

    # Definir layout da tabela de amostras
    samples_table_layout = [
        [sg.Table(
            values=[],
            headings=['Nome', 'L*', 'a*', 'b*'],
            key='-SAMPLES_TABLE-',
            auto_size_columns=False,
            justification='left',
            num_rows=8,
            col_widths=[20, 8, 8, 8],
            enable_events=True,
            select_mode=sg.TABLE_SELECT_MODE_BROWSE,
            vertical_scroll_only=False
        )]
    ]

    layout = [
        [sg.Text('LAB Color Chart', font=('Helvetica', 14, 'bold'), justification='center', expand_x=True)],
        [sg.Text('Informe os valores de L*a*b* para gerar o gráfico de cores CIELab:', 
                font=('Helvetica', 10), justification='center', expand_x=True)],
        
        [sg.Column([
            [sg.Frame('Amostra', [
                [sg.Text('Nome:', size=(8,1)), sg.Input(key='-SAMPLE_NAME-', size=(20,1), tooltip='Nome descritivo para a amostra')],
                [sg.Text('L*:', size=(8,1)), sg.Input(key='L', size=(10,1), tooltip='Valor de Luminosidade (0-100)')],
                [sg.Text('a*:', size=(8,1)), sg.Input(key='a', size=(10,1), tooltip='Valor de eixo a (-128 a 128)')],
                [sg.Text('b*:', size=(8,1)), sg.Input(key='b', size=(10,1), tooltip='Valor de eixo b (-128 a 128)')],
                [sg.Button('Adicionar', size=(10,1), button_color=('white', 'green'))],
                [sg.Button('Remover', size=(10,1), button_color=('white', 'red'))]
            ], size=(300, 200))],
        ], pad=(0,10)),
        
        sg.VSeparator(),
        
        sg.Column([
            [sg.Frame('Amostras Salvas', samples_table_layout, size=(430, 200))],
        ], pad=(0,10))],
        
        [sg.HorizontalSeparator()],
        
        [sg.Column([
            [sg.Button('Mostrar Gráfico', size=(15,1)), sg.Button('Limpar Tudo', size=(15,1))],
             [sg.Text()],
            [sg.Button('Calcular Delta E', size=(15,1))],
             [sg.Text()],
            [sg.Button('Referências', size=(10,1)), sg.Button('Sair', size=(10,1))]
        ], element_justification='center', expand_x=True)],
        [sg.Text()],
        [sg.HorizontalSeparator()],
        [sg.Text('2025 © LAB Color Chart v.3.0', font=('Arial', 8), justification='center', expand_x=True)]
    ]
    
    window = sg.Window('LAB Color Chart', layout, resizable=True, finalize=True)
    window.set_min_size((600, 530)) # Tamanho da janela principal

    # Ajustar tamanho da tabela quando a janela é redimensionada
    window['-SAMPLES_TABLE-'].expand(True, True)

    samples = []  # Lista para armazenar as amostras como dicionários

    def update_samples_table():
        table_data = []
        for sample in samples:
            table_data.append([
                sample.get('name', 'Sem nome'),
                f"{float(sample['L']):.2f}",
                f"{float(sample['a']):.2f}",
                f"{float(sample['b']):.2f}"
            ])
        window['-SAMPLES_TABLE-'].update(values=table_data)

    def update_arrays():
        L_valores = [float(s['L']) for s in samples]
        a_valores = [float(s['a']) for s in samples]
        b_valores = [float(s['b']) for s in samples]
        sample_names = [s.get('name', f'Amostra {i+1}') for i, s in enumerate(samples)]
        return L_valores, a_valores, b_valores, sample_names

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == 'Sair':
            break

        if event == 'Adicionar':
            try:
                name = values['-SAMPLE_NAME-'].strip() or f"Amostra {len(samples)+1}"
                L = values['L']
                a = values['a']
                b = values['b']
                
                if not L or not a or not b:
                    raise ValueError("Todos os campos L*, a* e b* devem ser preenchidos")
                
                # Validar valores numéricos e faixas
                L_val = float(L)
                a_val = float(a)
                b_val = float(b)
                
                if not (0 <= L_val <= 100):
                    raise ValueError("L* deve estar entre 0 e 100")
                if not (-128 <= a_val <= 128) or not (-128 <= b_val <= 128):
                    raise ValueError("a* e b* devem estar entre -128 e 128")
                
                samples.append({
                    'name': name,
                    'L': L,
                    'a': a,
                    'b': b
                })
                
                update_samples_table()
                window['-SAMPLE_NAME-'].update('')
                window['L'].update('')
                window['a'].update('')
                window['b'].update('')
                
            except ValueError as e:
                sg.popup_error(f"Erro: {str(e)}\nPor favor, insira valores válidos.")

        elif event == 'Remover':
            if values['-SAMPLES_TABLE-']:
                selected_index = values['-SAMPLES_TABLE-'][0]
                samples.pop(selected_index)
                update_samples_table()
            else:
                sg.popup_error("Nenhuma amostra selecionada para remover")

        elif event == '-SAMPLES_TABLE-':
            if values['-SAMPLES_TABLE-']:
                selected_index = values['-SAMPLES_TABLE-'][0]
                selected_sample = samples[selected_index]
                window['-SAMPLE_NAME-'].update(selected_sample.get('name', ''))
                window['L'].update(selected_sample['L'])
                window['a'].update(selected_sample['a'])
                window['b'].update(selected_sample['b'])

        elif event == 'Mostrar Gráfico':
            if samples:
                try:
                    L_valores, a_valores, b_valores, sample_names = update_arrays()
                    imagem_path = generate_color_wheel()
                    create_lab_color_chart(L_valores, a_valores, b_valores, imagem_path, sample_names)
                except Exception as e:
                    sg.popup_error(f"Erro ao gerar gráfico: {str(e)}")
            else:
                sg.popup_error("Adicione pelo menos uma amostra para mostrar o gráfico")

        elif event == 'Limpar Tudo':
            samples.clear()
            update_samples_table()
            window['-SAMPLE_NAME-'].update('')
            window['L'].update('')
            window['a'].update('')
            window['b'].update('')

        elif event == 'Calcular Delta E':
            delta_e_window()
            
        elif event == 'Referências':
            show_references()

    window.close()

if __name__ == "__main__":
    main()