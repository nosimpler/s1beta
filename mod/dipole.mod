: dipole.mod - mod file for range variable dipole
:
: v 0.4.0
: rev 2012-08-21 (SL: cleaned up and removed Qtotal, which was not used in earlier vers & redundant)
: last rev:

NEURON {
    SUFFIX dipole
    RANGE ri, ia, Q, ztan
    POINTER pv

    : for density. sums into Dipole at section position 1
    POINTER Qsum
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

    : human dipole order of 10nAm
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
