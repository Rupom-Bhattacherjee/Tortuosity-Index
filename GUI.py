#This is the code to create GUI interface for the app. 
#make sure you have all the libraries installed.
#As you can see this code is also calling several functions from the tortuosity_functions code. 
#So, you need to have this one on the same folder as well. 
#If you run this code you will see the app interface.
#but to create the exe file you need another library: auto-py-to-exe
#just run auto-py-to-exe on you terminal, it has gui interface, it will let you select the file you want to convert to an exe. 

import PySimpleGUI as sg
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
from Visualization_functions import plot_ti_wellname, plot_ti_pad,TI_wellname_line_plot
# Set the theme
sg.theme('LightGreen2')
# Define the GUI layout
layout = [
    [sg.Text('Welcome to the Tortuosity Index Launcher!', font='Helvetica 16 bold')],
    [sg.Text('Tortuosity Index is a metric used to evaluate the wellbore quality', font='Helvetica 12 bold')],
    [sg.Text('Instructions:', font='Helvetica 10 underline')],
    [sg.Text('1. Enter the required parameters based on how you want to visualize TI. Metric could be either Local/Inc/Azi/3D/3D_scaled')],
    [sg.Text('2. Section could be either lateral/vertical')],
    [sg.Text('3. Parameter "angle" is your inclination angle. If you select lateral section and angle 80, then the section> 80 will be displayed')],
    [sg.Text('4. If you select vertical section and angle 80, then the section< 80 will be displayed')],
    [sg.Text('5. If you want the entire wellbore to be displayed, select section=lateral and angle=0')],
    [sg.Text('Note: The plots will be displayed in separate windows.')],
    [sg.Text('------------------------------------------------------------------------', font='Helvetica 8')],
    [sg.Text('Select the method to plot tortuosity only after you set parameters:')],
    [sg.Button('Visualize TI along the wellbore by WellName'), sg.Button('Visualize TI along the wellbore by WellPad'), sg.Button('Plot TI against MD by WellName')],

    [sg.Text('Parameters for visualizing TI by WellName:')],
    [sg.Text('Metric:'), sg.Input(key='param2_1',default_text='3D',text_color='grey')],
    [sg.Text('WellName:'), sg.Input(key='param2_2',default_text='Y-Bar 1H',text_color='grey')],
    [sg.Text('Section:'), sg.Input(key='param2_3',default_text='vertical',text_color='grey')],
    [sg.Text('Angle:'), sg.Input(key='param2_4',default_text='20',text_color='grey')],

    [sg.Text('Parameters for visualizing TI by WellPad:')],
    [sg.Text('Metric:'), sg.Input(key='param3_1',default_text='3D',text_color='grey')],
    [sg.Text('WellPad:'), sg.Input(key='param3_2',default_text='WP000023 [KONE 7H, 8H]',text_color='grey')],
    [sg.Text('Section:'), sg.Input(key='param3_3',default_text='lateral',text_color='grey')],
    [sg.Text('Angle:'), sg.Input(key='param3_4',default_text='80',text_color='grey')],

    [sg.Text('Parameters for plotting TI against MD by WellName:')],
    [sg.Text('WellName:'), sg.Input(key='param4_1',default_text='Y-Bar 1H',text_color='grey')],
    [sg.Text('Section:'), sg.Input(key='param4_2',default_text='lateral',text_color='grey')],
    [sg.Text('Angle:'), sg.Input(key='param4_3',default_text='0',text_color='grey')],
    [sg.Output(size=(50, 10))],
    [sg.Canvas(key='plot_canvas')]
]

# Create the window
#window = sg.Window('Tortuosity Index Launcher by MOC', layout, finalize=True)
window = sg.Window('Tortuosity Index Launcher by MOC', layout, finalize=True, resizable=True, size=(1000, 800))

# Define global variables for the figure and canvas
fig = None
canvas = None

# Define a function to update the plot in the GUI window
def update_plot(fig, canvas):
    canvas.delete("all")
    plot_canvas = FigureCanvasTkAgg(fig, master=canvas)
    plot_canvas.draw()
    plot_canvas.get_tk_widget().pack()

# Event loop to process user inputs
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    elif event == 'Visualize TI along the wellbore by WellName':
        param2_1 = values['param2_1']
        param2_2 = values['param2_2']
        param2_3 = values['param2_3']
        param2_4 = values['param2_4']
        if not param2_1 or not param2_2 or not param2_3 or not param2_4:
            sg.popup_error('Please provide all the parameters for the "By WellName" method.', title='Error')
        else:
            try:
                param2_4 = float(param2_4)
                fig = plot_ti_wellname(param2_1, param2_2, param2_3, param2_4)
                canvas = window['plot_canvas'].TKCanvas
                threading.Thread(target=update_plot, args=(fig, canvas)).start()
            except Exception as e:
                sg.popup_error(str('Invalid Parameter Input. Please make sure the parameters you entered are correct and in right format. Check the database to know the right format!'), title='User Error')
    elif event == 'Visualize TI along the wellbore by WellPad':
        param3_1 = values['param3_1']
        param3_2 = values['param3_2']
        param3_3 = values['param3_3']
        param3_4 = values['param3_4']
        if not param3_1 or not param3_2 or not param3_3 or not param3_4:
            sg.popup_error('Please provide all the parameters for the "By WellPad" method.', title='Error')
        else:
            try:
                param3_4 = float(param3_4)
                fig = plot_ti_pad(param3_1, param3_2, param3_3,param3_4)
                canvas = window['plot_canvas'].TKCanvas
                threading.Thread(target=update_plot, args=(fig, canvas)).start()
            except Exception as e:
                sg.popup_error(str("Invalid Parameter Input. Please make sure the parameters you entered are correct and in right format. Check the database to know the right format!"), title='User Error')
    elif event == 'Plot TI against MD by WellName':
            param4_1 = values['param4_1']
            param4_2 = values['param4_2']
            param4_3 = values['param4_3']
            if not param4_1 or not param4_2 or not param4_3:
                sg.popup_error('Please provide all the parameters for the "plot TI vs MD by WellName" method.', title='Error')
            else:
                try:
                    param4_3 = float(param4_3)
                    fig = TI_wellname_line_plot(param4_1, param4_2, param4_3)
                    canvas = window['plot_canvas'].TKCanvas
                    threading.Thread(target=update_plot, args=(fig, canvas)).start()
                except Exception as e:
                    sg.popup_error(str("Invalid Parameter Input. Please make sure the parameters you entered are correct and in right format. Check the database to know the right format!"), title='User Error')
# Close the window
window.close()
