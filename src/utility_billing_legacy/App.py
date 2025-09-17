#%%
import os
import sys
import pandas as pd
import numpy as np
import CalcUtilityBillings as cb
import InvoiceGenerator as ig
import numpy as np

#%%
def main (): 
    name = None
    rr = None
    gl = None
    pdF = None
    for i in range(1, len(sys.argv)):
        if sys.argv[i] == '-rr':
            rr = sys.argv[i+1]
        elif sys.argv[i] == '-gl':
            gl = sys.argv[i+1]
        elif sys.argv[i] == '-pdf':
            pdF = sys.argv[i+1]
        elif sys.argv[i] == '-n':
            name = sys.argv[i+1]
    calc = cb.CalcUtilityBillings(rr, gl, pdF)
    bdf = calc.calcBillings()
    cdf = calc.getTenantChargeImportDataframe(bdf)
    propDF = calc.property_df
    big = ig.InvoiceGenerator(bdf, calc.billing_cycle_start_date, calc.billing_cycle_end_date, "./ITEX_logo.png", propDF, f"{name}_invoices.pdf")
    big.generate_invoices()
    bdf.to_excel(f"{name}_bdf.xlsx", index=False) 
    cdf.to_excel(f"{name}_cdf.xlsx", index=False)
#%%
if __name__ :
    main()