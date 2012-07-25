NEURON {
    : SUFFIX dipole
    POINT_PROCESS Dipole
    RANGE ri, ia, Q, ztan
    POINTER pv

    : for density. sums into Dipole at section position 1
    : POINTER Qsum

    : for POINT_PROCESS. Gets additions from dipole
    RANGE Qsum

    : to allow Vector record of total in a process
    POINTER Qtotal
}

UNITS {
    (nA)   = (nanoamp)
    (mV)   = (millivolt)
    (Mohm) = (megaohm)
    (um)   = (micrometer)
    (Am)   = (amp meter)
    (fAm)  = (femto amp meter)
}

ASSIGNED {
    ia (nA)
    ri (Mohm)
    pv (mV)
    v (mV)
    ztan (um)
    Q  (fAm)
    Qsum (fAm)
    Qtotal (fAm)
}

: solve for v's first then use them
AFTER SOLVE {
    ia = (pv - v) / ri
    Q = ia * ztan
    Qsum = Qsum + Q
    Qtotal = Qtotal + Q
}
    
AFTER INITIAL {
    ia = (pv - v) / ri
    Q = ia * ztan
    Qsum = Qsum + Q
    Qtotal = Qtotal + Q
}

: following needed for POINT_PROCESS only but will work if also in SUFFIX
 BEFORE INITIAL {
    Qsum = 0
    Qtotal = 0
 }

 BEFORE BREAKPOINT {
    Qsum = 0
    Qtotal = 0
 }
