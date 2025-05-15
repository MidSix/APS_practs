#!/usr/bin/env python

import sys
import array
import socket
import ipaddress

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['axes.spines.top'] = False
mpl.rcParams['mathtext.default'] = 'regular'
mpl.rcParams['savefig.format'] = 'svg'


PORT = 80


IP='192.168.18.206'   # configurar al valor impreso por el ESP32
SAMPLE_RATE=10240  # en Hz
BSIZE=1024  # en muestras
FILTER=np.array([1.0], dtype='float32')  # por defecto una delta (dtype debe ser float32!)

exit = False

def on_resize(event):
    global bg
    plt.tight_layout()
    fig.canvas.draw()
    bg = fig.canvas.copy_from_bbox(fig.bbox)

def on_key(event):
    global exit
    if event.key == 'q':
        exit = True


### main
def main():
    global bg, plt, fig

    try:
        ipaddress.ip_address(IP)
    except:
        print(f'IP {IP} inválida')
        return 1

    if SAMPLE_RATE < 8000 or SAMPLE_RATE > 48000:
        print(f'Tasa de muestreo {SAMPLE_RATE} inválida, debe estar en [8000...48000]')
        return 1
        
    if BSIZE < 64 or BSIZE > 2048:
        print(f'Tamaño de bloque {BSIZE} inválido, debe estar en [64...2048]')
        return 1

    if len(FILTER) > 64 or FILTER.dtype != np.float32:
        print(f'Filtro {FILTER} inválido, debe ser un array de tamaño <= 64 de tipo float32')
        return 1

    # conectamos a la IP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP, PORT))

    # enviamos la solicitud
    msg = bytearray()
    msg += (4 + 4 + 4 + 4 * len(FILTER)).to_bytes(4, 'little')
    msg += SAMPLE_RATE.to_bytes(4, 'little')
    msg += BSIZE.to_bytes(4, 'little')
    msg += FILTER.tobytes()
    s.send(msg)
    
    plt.ion()

    fig = plt.figure("FFT")
    fig.add_subplot(111)
    line, = fig.axes[0].plot([], [], 'red', animated=True)
    fig.axes[0].set_ylim(0, 1)

    fig.canvas.mpl_disconnect(fig.canvas.manager.key_press_handler_id)  # remove defaults
    fig.canvas.mpl_connect('resize_event', on_resize)
    fig.canvas.mpl_connect('key_press_event', on_key)

    plt.tight_layout()
    fig.canvas.draw()
    bg = fig.canvas.copy_from_bbox(fig.bbox)

    packet = bytearray()
    i = 0

    fft_size = BSIZE
    x = np.linspace(-SAMPLE_RATE//2, SAMPLE_RATE//2, fft_size)

    fig.axes[0].set_xlim(x[0], x[-1])
    while True:
        if exit:
            s.close()
            break
        data = s.recv(fft_size * 4)
        i += len(data)
        if not data: 
            break
        data_str = ' '.join('{:02x}'.format(x) for x in data[0:8])
        print(f'{len(data)}: {data_str}')
        end = fft_size * 4 - len(packet)
        packet.extend(data[:end])
        if len(packet) == fft_size * 4:
            y_arr = array.array('f', packet)
            y_left = y_arr[BSIZE//2:]
            y_right = y_arr[:BSIZE//2]
            y_shifted = y_left + y_right
            y = np.array(y_shifted) / (max(BSIZE * 2**12, max(y_shifted)))
            y[0] = 0
            line.set_data(x, y)
            fig.canvas.restore_region(bg)
            fig.draw_artist(line)
            fig.canvas.blit(fig.bbox)
            fig.canvas.flush_events()
            packet = bytearray(data[end:])

if __name__ == '__main__':
    sys.exit(main())

