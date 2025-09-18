import os
import pandas as pd
import numpy as np
from numpy import datetime64
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

class CalcUtilityBillings :

    tax_rate = 0.0825

    base_fee_owner = 0.50

    base_fee_to_resident = 4.50

    billing_cycle_period = "monthly"

    billing_cycle_start_date = None

    billing_cycle_end_date = None

    billing_cycle_days = 30

    rent_roll_df = None

    rent_roll_xls_file = ""

    gl_billing_xls_file = ""

    property_data_file = ""

    gl_df = None

    billings_df = None

    adj_df = None
    
    def __init__(self, 
            rentRollFileName,
            glFileName,
            pdFile
        ) :
        
        self.tax_rate = 0.0825

        self.base_fee_owner = 0.50

        self.base_fee_to_resident = 4.50

        self.base_fee_ar_gl_code = 12011

        self.base_fee_gl_code = 42143

        self.billing_cycle_period = "monthly"

        self.billing_cycle_days = 30

        self.rent_roll_xls_file = rentRollFileName

        self.gl_billing_xls_file = glFileName

        self.gl_df = self.getPandasDFFromXls(glFileName)

        self.property_data_file = pdFile

        self.property_df = self.getPropertyData(pdFile)

        self.unit_mix_df = self.get_unit_mix_df(pdFile)

        self.rent_roll_df = self.getRentRoll()

        self.billings_df = None   
        
        self.adj_df = self.get_adj_df(pdFile)


    def getPandasDFFromXls(self, xlsFile) :
        return pd.read_excel(xlsFile)

    #Remove to use strict schema reader below
    # def getRentRoll(self) :
    #     rrXls = self.rent_roll_xls_file
    #     df = pd.read_excel(rrXls, sheet_name="Report1", header=4)
    #     # Temp test Adjustment, removed the following from pd.read_excel    ,  dtype={'Unit':str, 'Unit Type':str, 'Unit.1':str, 'Resident':str, 'Name':str, 'Market':str, 'Actual':str, 'Deposit':str, 'Other_Deposit':str, 'Move In':datetime, 'Lease':datetime, 'Move Out':datetime, 'Balance':str})
    #     # df.columns = df.iloc[0:1].apply(lambda x: '_'.join(str(x).strip()))
    #     df = df.dropna(subset=['Resident', 'Unit Type'])
    #     df = df.drop_duplicates(subset=['Unit'])
    #     df = df.rename(columns={'Unit Type':'Unit_Type', 'Unit.1': 'SqFt', 'Actual':'Rent', 'Lease':'Lease_Exp', 'Move In':'Move_In', 'Move Out':'Move_Out', 'Resident.1':'Resident_Deposit'})
    #     df['Move_In'] = pd.to_datetime(df['Move_In'], errors='coerce')
    #     df['Move_Out'] = pd.to_datetime(df['Move_Out'], errors='coerce')
    #     df['Lease_Exp'] = pd.to_datetime(df['Lease_Exp'], errors='coerce')
    #     df['SqFt'] = df['SqFt'].astype(int)
    #     df['Rent'] = df['Rent'].astype(int)

    #     self.rent_roll = df
    #     return df

    def getRentRoll(self):
        rrXls = self.rent_roll_xls_file
        xlf = pd.ExcelFile(rrXls)
        # Prefer "Report1" if present, otherwise use the first sheet
        sheet = "Report1" if "Report1" in xlf.sheet_names else xlf.sheet_names[0]

        # Try header at row 5 (index 4). If that fails, fall back to row 1.
        try:
            df = pd.read_excel(xlf, sheet_name=sheet, header=4)
        except Exception:
            df = pd.read_excel(xlf, sheet_name=sheet, header=0)

        df = df.dropna(subset=["Resident", "Unit Type"])
        df = df.drop_duplicates(subset=["Unit"])
        df = df.rename(columns={
            "Unit Type": "Unit_Type",
            "Unit.1": "SqFt",
            "Actual": "Rent",
            "Lease": "Lease_Exp",
            "Move In": "Move_In",
            "Move Out": "Move_Out",
            "Resident.1": "Resident_Deposit",
        })
        df["Move_In"]   = pd.to_datetime(df["Move_In"], errors="coerce")
        df["Move_Out"]  = pd.to_datetime(df["Move_Out"], errors="coerce")
        df["Lease_Exp"] = pd.to_datetime(df["Lease_Exp"], errors="coerce")
        df["SqFt"] = pd.to_numeric(df["SqFt"], errors="coerce").fillna(0).astype(int)
        df["Rent"] = pd.to_numeric(df["Rent"], errors="coerce").fillna(0).astype(int)

        self.rent_roll = df
        return df

    # Removed to use strict schema reader below
    # def getPropertyData(self, pdfile) :
    #     df = pd.read_excel(pdfile, usecols="A:O", sheet_name='propertydata', dtype={ 'property_code':str, 'property_name':str, 'address1':str,'address2':str, 
    #                                                         'city':str, 'state':str, 'zip':str, 'phone':str, 'primary_contact':str, 
    #                                                         'email':str, 'website':str, 'gross_sf':int, 'net_sf':int, 'ttl_occ':int, 'disable_fee':str })
    #     self.property_df = df

    #     self.unit_mix_df = pd.read_excel(pdfile, usecols="A:F", sheet_name='unitmix', dtype={'Unit_Type':str, 'name':str, 'avg_sf':int, 'avg_rent':int, 'units':int, 'occ':float })                   
    #     return df
    
    # New strict schema reader for Property Data
    def getPropertyData(self, pdfile):
        def pick(sheet_names, want):
            # case/space-insensitive match; fallback to first sheet
            norm = {s: s.lower().replace(" ", "") for s in sheet_names}
            key  = want.lower().replace(" ", "")
            for s, n in norm.items():
                if n == key:
                    return s
            return sheet_names[0]

        xlf = pd.ExcelFile(pdfile)

        s_prop = pick(xlf.sheet_names, "propertydata")
        s_mix  = pick(xlf.sheet_names, "unitmix")
        s_adj  = pick(xlf.sheet_names, "adjustments")

        df = pd.read_excel(pdfile, usecols="A:O", sheet_name=s_prop)
        self.property_df = df

        self.unit_mix_df = pd.read_excel(pdfile, usecols="A:F", sheet_name=s_mix)
        self.adj_df      = pd.read_excel(pdfile, usecols="A:B", sheet_name=s_adj)

        # Basic coercions (won’t fail if col missing)
        for c in ["gross_sf","net_sf","ttl_occ"]:
            if c in self.property_df.columns:
                self.property_df[c] = pd.to_numeric(self.property_df[c], errors="coerce").fillna(0).astype(int)
        if "occ" in self.unit_mix_df.columns:
            self.unit_mix_df["occ"] = pd.to_numeric(self.unit_mix_df["occ"], errors="coerce")

        return self.property_df

    def get_unit_mix_df(self, pdFile) :
        df = pd.read_excel(pdFile, usecols="A:F", sheet_name='unitmix', dtype={'Unit_Type':str, 'name':str, 'avg_sf':int, 'avg_rent':int, 'units':int, 'occ':float })                   
        self.unit_mix_df= df
        return df
    
    def get_adj_df(self, pdFile) :
        df = pd.read_excel(pdFile, usecols="A:B", sheet_name='adjustments', dtype={'type':str, 'adj_rate':float })                   
        self.adj_df = df
        return df

    # Removed to use strict schema reader below
    # def getGLBillings(self) :
    #     glXls = self.gl_billing_xls_file
    #     df = pd.read_excel(glXls, sheet_name="Report1", usecols="A:k", dtype={'gl_code':int, 'ar_gl_code':int, 'type':str, 'notes':str, 'expense_GL_code':int, 'property_code':str, 
    #                                                                           'billing_period_start':datetime64, 'billing_period_end':datetime64,
    #                                                                           'amount':float, 'charge_date':datetime64, 'post_month':datetime64})
    #     self.gl_df = df
    #     return df

    # New strict schema reader for GL Billings
    def getGLBillings(self):
        glXls = self.gl_billing_xls_file
        xlf = pd.ExcelFile(glXls)
        sheet = "Report1" if "Report1" in xlf.sheet_names else xlf.sheet_names[0]

        df = pd.read_excel(
            xlf, sheet_name=sheet, usecols="A:K"
        )
        # Coerce expected columns
        for c in ["amount"]
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")
        for c in ["billing_period_start", "billing_period_end", "charge_date", "post_month"]:
            if c in df.columns:
                df[c] = pd.to_datetime(df[c], errors="coerce")

        # Ensure expected text/ids exist (won’t error if columns missing)
        for c in ["gl_code","ar_gl_code","type","notes","property_code"]:
            if c in df.columns:
                df[c] = df[c]

        self.gl_df = df
        return df


    def getTotalSqFt(self) :
        if self.rent_roll_df is None :
            self.getRentRoll()

        rrdf = self.rent_roll_df
        totalSqft = rrdf["SqFt"].values.sum() 
        return totalSqft    
    

    def calcBillings(self) :
        if self.rent_roll_df is None :
            self.getRentRoll()
        
        # Removing generic reader of GL Billings
        # if self.gl_df is None :
        #     self.getGLBillings()
        
         # Always load GL with the strict schema  (NEW)
        gl_billings_df = self.getGLBillings().copy()    # <- uses proper sheet/dtypes
        
        totalSqft = self.getTotalSqFt()
        billings_df = pd.DataFrame()

        # Removed section below that was associated with old generic reader of GL Billings
        # get the gl_billings 
        # gl_billings_df = self.gl_df
                
        rent_roll_df = self.rent_roll_df.dropna(subset='Name')
        
        billing_period_start = gl_billings_df['billing_period_start'].iloc[0]
        billing_period_end = gl_billings_df['billing_period_end'].iloc[0]
        if self.property_df is None :
            self.getPropertyData(self.property_data_file)
        if self.unit_mix_df is None :
            self.get_unit_mix_df(self.property_data_file)
        if self.adj_df is None :
            self.adj_df = self.get_adj_df(self.property_data_file)
        gl_billings_df = pd.merge(gl_billings_df, self.adj_df, on='type', how='left')
        
        # NEW: ensure numeric + datetime dtypes
        gl_billings_df["amount"]   = pd.to_numeric(gl_billings_df["amount"], errors="coerce").fillna(0.0)
        gl_billings_df["adj_rate"] = pd.to_numeric(gl_billings_df["adj_rate"], errors="coerce").fillna(1.0)

        gl_billings_df["billing_period_start"] = pd.to_datetime(gl_billings_df["billing_period_start"], errors="coerce")
        gl_billings_df["billing_period_end"]   = pd.to_datetime(gl_billings_df["billing_period_end"], errors="coerce")
        gl_billings_df["charge_date"]          = pd.to_datetime(gl_billings_df["charge_date"], errors="coerce")
        gl_billings_df["post_month"]           = pd.to_datetime(gl_billings_df["post_month"], errors="coerce")
        
        property_df = self.property_df
        unit_mix_df = self.unit_mix_df
        ttl_occ = property_df['ttl_occ'].iloc[0]

        gross_sf = property_df['gross_sf'].iloc[0]
        net_sf = property_df['net_sf'].iloc[0]
        state = property_df['state'].iloc[0]
        perc_ttl_sqft = net_sf / gross_sf

        # merge rent roll and unit_mix_df on Unit_Type
        rent_roll_df = pd.merge(rent_roll_df, unit_mix_df, on='Unit_Type', how='left')

        # loop through each rr & then add each gl calc into that row. Then append it to the billings_df
        for rr_index, rr_row in rent_roll_df.iterrows() :
            if(rr_row['Name'] is not None and rr_row['Name'] != 'nan'  and rr_row['Unit'] != 'nan' and str(rr_row['Name']).strip().upper != 'VACANT' and str(rr_row['Name']).strip().upper != 'MODEL' and str(rr_row['Name']).strip().upper != 'DOWN') :
                if(rr_row['Resident'] != 'VACANT' and rr_row['Resident'] != 'MODEL' and rr_row['Resident'] != 'DOWN') :
                    t_sqft = rr_row['SqFt']
                    perc_sqft = t_sqft / totalSqft
                    occ = rr_row['occ']
                    perc_occ = occ / ttl_occ
                    Tenant_Name = rr_row['Name']
                    Resident = rr_row['Resident']
                    Unit = rr_row['Unit']
                    SqFt = rr_row['SqFt']
                    Rent = rr_row['Rent']
                    Move_Out_Date = rr_row['Move_Out']
                    Move_In_Date = rr_row['Move_In']
                    
                    #Removing section of old code that was not working properly
                    # perc_month = 100
                    # if billing_period_start is datetime64 :
                    #     billing_period_start = self.convert_datetime64_to_datetime(billing_period_start)
                    # if billing_period_end is datetime64 :
                    #     billing_period_end = self.convert_datetime64_to_datetime(billing_period_end)
                    # if Move_Out_Date is not datetime :
                    #     Move_Out_Date = billing_period_end + relativedelta(months=1)
                    # perc_month = self.percentage_days_in_period(billing_period_start, billing_period_end, Move_In_Date, Move_Out_Date)
                    #print('Tenant: ' + str(rr_row['Resident']) + '  billing_period_start: ' + str(billing_period_start) + '  billing_period_end: ' + str(billing_period_end) + ' Move_In_Date: ' + str(Move_In_Date) + ' Move_Out_Date: ' + str(Move_Out_Date) + ' perc_month: ' + str(perc_month))
                    # perc_month = perc_month / 100
                    
                    # New code to calculate perc_month
                    # --- ensure proper datetime types for the period and move dates ---
                    # Normalize billing period dates (from GL) to real datetime.datetime
                    billing_period_start = pd.to_datetime(billing_period_start).to_pydatetime()
                    billing_period_end   = pd.to_datetime(billing_period_end).to_pydatetime()

                    # Normalize resident dates (may be NaT) to pandas Timestamps or NaT
                    Move_In_Date  = pd.to_datetime(Move_In_Date,  errors="coerce")
                    Move_Out_Date = pd.to_datetime(Move_Out_Date, errors="coerce")

                    # Compute percentage of month occupied during the billing period
                    perc_month = self.percentage_days_in_period(
                        billing_period_start,
                        billing_period_end,
                        Move_In_Date,
                        Move_Out_Date
                    )

                    # Guard: if something went wrong and a string came back, default to full month
                    if isinstance(perc_month, str):
                        perc_month = 100.0

                    # Convert percent to fraction
                    perc_month = perc_month / 100.0
                
                    
                    charge_date = None
                    post_month = None
                    for gl_index, gl_row in gl_billings_df.iterrows() :
                        gl_ix = gl_row['type']
                        if 'reading_prev' not in gl_row.index :
                            reading_prev = None
                        else :
                            reading_prev = gl_row['reading_prev']
                        if 'reading_current' not in gl_row.index :
                            reading_current = None
                        else :
                            reading_current = gl_row['reading_current']

                        if 'charge_date' in gl_row.index :
                            charge_date = gl_row['charge_date']
                        if 'post_month' in gl_row.index :
                            post_month = gl_row['post_month']
                        
                        # Remove the old bill_due_date code to normalize to datetime at the source
                        # if 'bill_due_date' in gl_row.index :
                        #     bill_due_date = gl_row['bill_due_date']
                        # else :
                        #     bill_due_date = datetime.today().strftime('%m/%d/%Y')

                        if 'bill_due_date' in gl_row.index:
                            bill_due_date = pd.to_datetime(gl_row['bill_due_date'], errors='coerce')
                        else:
                            bill_due_date = pd.Timestamp.today().normalize()

                        # get the adj_rate
                        if 'adj_rate' in gl_row.index :
                            adj_rate = gl_row['adj_rate'] 
                        else :
                            adj_rate = 1

                        # get the proration of based upon the square footage and adj_rate

                        gl_amount = gl_row['amount'] * perc_ttl_sqft * adj_rate

                        # if this is in Texas and is water or sewer then we need to use the option 4 calculation
                        if state == 'TX' and (gl_ix == 'water' or gl_ix == 'sewerbil') :
                            # get 50% of the gl_amount
                            gl_amount_50 = gl_amount * 0.5
                            amount_sf = perc_sqft * gl_amount_50 * perc_month
                            amount_occ = perc_occ * gl_amount_50 * perc_month
                            amount = amount_sf + amount_occ
                        else : 
                            # if we are not in Texas or this is not water or sewer then we use the normal calculation
                            amount = perc_sqft * gl_amount * perc_month
                    
                        gl_notes = gl_row['notes'] + ' ' + str(gl_row['billing_period_start'].strftime('%m/%d/%Y')) + ' to ' + str(gl_row['billing_period_end'].strftime('%m/%d/%Y'))
                    
                        billings_row_s = { 'Unit':Unit, 'Resident':Resident, 'Name':Tenant_Name, 'SqFt':SqFt, 'Rent':Rent, 'code':gl_ix, 'perc_sqft':perc_sqft,
                                        'amount':amount, 'gl_code':gl_row['gl_code'], 'ar_gl_code':gl_row['ar_gl_code'], 'gl_notes':gl_notes, 'gl_billing_period_start':gl_row['billing_period_start'], 
                                'gl_billing_period_end':gl_row['billing_period_end'], 'gl_reading_prev':reading_prev, 'gl_reading_current':reading_current, 'charge_date':charge_date, 
                                'post_month':post_month, 'bill_due_date':bill_due_date, 'move_in':Move_In_Date, 'move_out':Move_Out_Date, 'perc_month':perc_month }
                        
                        billings_row = pd.Series(billings_row_s).to_frame().T
                        billings_df = pd.concat([billings_df, billings_row], ignore_index=True)
                    # add the base fee
                    if 'disable_fee' in property_df.columns :
                        disable_fee = property_df['disable_fee'].iloc[0]
                    else :
                        disable_fee = 'N'
                    if disable_fee != 'Y' :
                        billings_row_bf = { 'Unit':Unit, 'Resident':Resident, 'Name':Tenant_Name, 'SqFt':SqFt, 'Rent':Rent, 'code':'Utility', 'perc_sqft':perc_sqft,
                                            'amount':self.base_fee_to_resident, 'gl_code':self.base_fee_gl_code, 'ar_gl_code':self.base_fee_ar_gl_code, 
                                            'gl_notes':'Tenant Service Fee ' + str(gl_row['billing_period_start'].strftime('%m/%d/%Y')) + ' to ' + str(gl_row['billing_period_end'].strftime('%m/%d/%Y')), 
                                            'gl_billing_period_start':gl_row['billing_period_start'], 
                                            'gl_billing_period_end':gl_row['billing_period_end'], 'gl_reading_prev':reading_prev, 'gl_reading_current':reading_current, 'charge_date':charge_date, 
                                            'post_month':post_month, 'bill_due_date':bill_due_date, 'move_in':Move_In_Date, 'move_out':Move_Out_Date, 'perc_month':perc_month }
                        billings_row = pd.Series(billings_row_bf).to_frame().T
                        billings_df = pd.concat([billings_df, billings_row], ignore_index=True)
                    self.billing_cycle_start_date = gl_row['billing_period_start']
                    self.billing_cycle_end_date = gl_row['billing_period_end']
                    
    
        self.billings_df = billings_df
        
        # now that we have the new dataset
        return billings_df
    
    def same_month(self, date1, date2):
        return date1.year == date2.year and date1.month == date2.month


    from datetime import datetime, timedelta
    def percentage_days_in_period(self, billing_period_start_date, billing_period_end_date, move_in_date, move_out_date):
        # make sure billing_period_start_date and billing_period_end_date are datetime objects
        if not isinstance(billing_period_start_date, datetime) or not isinstance(billing_period_end_date, datetime):
            return "billing_period_start_date and/or billing_period_end_date are not datetime objects"

        days_in_period = (billing_period_end_date - billing_period_start_date).days + 1
        
        # set dates to outside of current billing period if they're not datetime objects
        if not isinstance(move_in_date, datetime):
            move_in_date = billing_period_start_date - timedelta(days=1)
        if not isinstance(move_out_date, datetime):
            move_out_date = billing_period_end_date + timedelta(days=1)

        if move_in_date > billing_period_end_date or move_out_date < billing_period_start_date:
            return 100
        else:
            actual_move_in_date = max(move_in_date, billing_period_start_date)
            actual_move_out_date = min(move_out_date, billing_period_end_date)
            days_moved_in = (actual_move_out_date - actual_move_in_date).days + 1
            return (days_moved_in / days_in_period) * 100


    def convert_datetime64_to_datetime(self, dt64):
        if isinstance(dt64, np.datetime64):
            dt = dt64.astype(datetime)
            return dt
        else:
            raise ValueError("Input must be a numpy.datetime64 object.")


    def getTenantChargeImportDataframe(self, billings_dataframe) :
        # format dataframe into a new dataframe 
        # #Always_C, Tenant_Code, , Charge_Date, Post_Month, Charge_Reference, Description, Property_Code, Amount, Charge_GL_Code,	AR_GL_Code,	Charge_Code
        tc_df = pd.DataFrame(columns=['Always C', 'Charge #', 'Tenant Code', '', 'Charge Date', 'Post Month', 'Charge Reference', 'Description/Notes (Posts to ledger)', 'Property Code', 'Amount', 'Charge GL Code','AR GL Code','Charge Code'])
        charge_num = 1
        property_df = self.property_df
        for index, row in billings_dataframe.iterrows() :
            charge_date = row['charge_date']
            post_month = row['post_month']
            post_month_str = post_month.strftime('%m/%Y') if pd.notna(post_month) else ''
            tc_row = { 'Always C':'C', 'Charge #': charge_num, 'Tenant Code':row['Resident'], 
                      '':'', 'Charge Date':charge_date, 'Post Month':post_month_str, 
                      'Charge Reference':row['code'], 'Description/Notes (Posts to ledger)':row['gl_notes'], 'Property Code':property_df.loc[0]['property_code'], 
                      'Amount':row['amount'], 'Charge GL Code':row['gl_code'],'AR GL Code':row['ar_gl_code'],'Charge Code':row['code']}
            tc_row = pd.Series(tc_row).to_frame().T
            tc_df = pd.concat([tc_df, tc_row], ignore_index=True)
            charge_num += 1
        return tc_df
    
    