: dipole_pp.mod - creates point process mechanism Dipole
:
: v 0.4.0
: rev 2012-08-21 (SL: cleaned up and removed Qtotal)
: last rev: 

NEURON {
    POINT_PROCESS Dipole
    RANGE ri, ia, Q, ztan
    POINTER pv

    : for POINT_PROCESS. Gets additions from dipole
    RANGE Qsum
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
}

: solve for v's first then use them
AFTER SOLVE {
    ia = (pv - v) / ri
    Q = ia * ztan
    Qsum = Qsum + Q
}
    
AFTER INITIAL {
    ia = (pv - v) / ri
    Q = ia * ztan
    Qsum = Qsum + Q
}

: following needed for POINT_PROCESS only but will work if also in SUFFIX
 BEFORE INITIAL {
    Qsum = 0
 }

 BEFORE BREAKPOINT {
    Qsum = 0
 }
