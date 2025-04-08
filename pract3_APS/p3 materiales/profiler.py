
class Profiler:
    def __init__(self):
        self.s = 'Tiempo bloque: {} µs (captura: {} µs; procesado: {} µs; envío: {} µs)'        
        self.reset()
        
    def reset(self):
        self.prev_t0 = 0
        self.tot_t = 0
        self.tot_d_cap = 0
        self.tot_d_proc = 0
        self.tot_d_send = 0
        self.tot_meas = -5
        
    def print_partial(self, t0, t_cap=-1, t_proc=-1, t_send=-1):
        d_cap = t_cap - t0 if t_cap != -1 else 0
        d_proc = t_proc - t_cap if t_proc != -1 else 0
        d_send = t_send - t_proc if t_send != -1 else 0
        print(self.s.format(t0-self.prev_t0, d_cap, d_proc, d_send))
        if self.tot_meas >= 0:
            self.tot_t += t0 - self.prev_t0
            self.tot_d_cap += d_cap
            self.tot_d_proc += d_proc
            self.tot_d_send += d_send
        self.prev_t0 = t0
        self.tot_meas += 1
       
    def print_average(self):
        if self.tot_meas < 0:
            return
        print(self.s.format(self.tot_t/self.tot_meas, self.tot_d_cap/self.tot_meas,
                            self.tot_d_proc/self.tot_meas, self.tot_d_send/self.tot_meas))        
        self.reset()
