"""
Data loading and processing functions.
"""

import pandas as pd
import ast
import numpy as np

from config import DATA_PATH



def import_raw_data(file_path=DATA_PATH):
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error importing data: {e}")
        return pd.DataFrame()
    
    
    


def get_timeline_data(df):
    """
    Prepares and returns timeline data from the provided DataFrame.
    
    Parameters:
        df (pd.DataFrame): The input DataFrame containing raw data.
    Returns:
        pd.DataFrame: A DataFrame formatted for timeline visualization.
    """
    timeline = timelinedata(df)

    # call select_columns (handle variants: no-arg, df-arg, or returns self)
    try:
        selected = timeline.select_columns()
    except TypeError:
        selected = timeline.select_columns(df)

    # call format_calc_df (handle variants: method on returned object, or requires dataframe argument)
    if hasattr(selected, 'format_calc_df'):
        try:
            data = selected.format_calc_df()
        except TypeError:
            data = selected.format_calc_df(df)
    else:
        try:
            data = timeline.format_calc_df(selected)
        except TypeError:
            data = timeline.format_calc_df()
            
    return data






















class timelinedata:
    """
    Object-oriented wrapper for timeline data processing.
    Instantiate with a pandas DataFrame or set with set_df().
    Methods operate on the internal DataFrame or on an optionally provided DataFrame.
    """

    def __init__(self, df=None):
        self.df = df.copy() if df is not None else pd.DataFrame()

    def set_df(self, df):
        self.df = df.copy()

    def select_columns(self, columns=['seao_id','tender_title', 'buyer_name', 'date_debut', 'date_fin','duration_base','opt','duration_tot','lots_name','awards_suppliers_name','awards_amount'], df=None):
        """
        Selects specific columns from a DataFrame.
        """
        data = self.df if df is None else df
        if data is None or data.empty:
            return pd.DataFrame()
        return data[columns] if all(col in data.columns for col in columns) else pd.DataFrame()

    def process_options(self, df=None):
        """
        Processes optional contract periods in the DataFrame.
        Duplicate rows where opt==1 to create base and option periods.
        Returns processed DataFrame (and updates internal df if df is None).
        """
        data = (self.df if df is None else df).copy()
        if data.empty:
            if df is None:
                self.df = data
            return data

        # ensure date_debut is datetime for offset math
        data['date_debut'] = pd.to_datetime(data['date_debut'], errors='coerce')
        data = data.reset_index(drop=True)

        result = data.copy()  # will accumulate new rows
        for i in range(len(data)):
            opt_val = data.at[i, 'opt']
            # normalize option to integer 0/1 (handle strings/nan)
            try:
                option = int(opt_val)
            except Exception:
                try:
                    option = int(ast.literal_eval(str(opt_val)))
                except Exception:
                    option = 0

            if option != 1:
                continue

            date_debut = data.at[i, 'date_debut']
            duration_base = data.at[i, 'duration_base']
            duration_tot = data.at[i, 'duration_tot']

            # if any required values are missing, skip
            if pd.isna(date_debut) or pd.isna(duration_base) or pd.isna(duration_tot):
                continue

            try:
                dur_base = int(duration_base)
                dur_tot = int(duration_tot)
            except Exception:
                continue

            # compute base end and optional end using DateOffset
            new_date_fin_base = date_debut + pd.DateOffset(months=dur_base)
            new_start = new_date_fin_base
            new_end = date_debut + pd.DateOffset(months=dur_tot)

            # update base row in result (set opt 0)
            # find the corresponding row in result by matching original index and date_debut
            result_idx = result[(result.index == i)].index
            if not result_idx.empty:
                ridx = result_idx[0]
                result.at[ridx, 'date_fin'] = new_date_fin_base
                result.at[ridx, 'duration_days'] = (new_date_fin_base - date_debut).days
                result.at[ridx, 'opt'] = 0
            else:
                # fallback: update original data copy
                data.at[i, 'date_fin'] = new_date_fin_base
                data.at[i, 'duration_days'] = (new_date_fin_base - date_debut).days

            # create duplicate row for the optional period
            new_row = data.loc[i].copy()
            new_row['date_debut'] = new_start
            new_row['date_fin'] = new_end
            new_row['duration_days'] = (new_end - new_start).days
            new_row['opt'] = 1

            # append the new row
            result = pd.concat([result, new_row.to_frame().T], ignore_index=True)

        result['pattern'] = result['opt'].apply(lambda x: 'Base du contrat' if int(x) == 0 else 'Options du contrat')
        if df is None:
            self.df = result
        return result

    @staticmethod
    def format_awards_amount(x):
        """
        Formats award amounts for display.
        """
        if pd.isna(x) or x == '' or x == '[]' or x == '0' or x == 0:
            return 'Inconnu'
        if isinstance(x, str):
            try:
                parsed = ast.literal_eval(x)
                x = parsed
            except Exception:
                s = ''.join(ch for ch in x if ch.isdigit() or ch in '.,')
                if s == '':
                    return 'Inconnu'
                try:
                    num = float(s.replace(',', ''))
                    return f"{num:,.0f} $"
                except Exception:
                    return 'Inconnu'
        if isinstance(x, (list, tuple, np.ndarray)):
            formatted = []
            for v in x:
                if pd.isna(v) or v == '':
                    continue
                try:
                    num = float(v)
                    formatted.append(f"{num:,.0f} $")
                except Exception:
                    s = ''.join(ch for ch in str(v) if ch.isdigit() or ch in '.,')
                    if s == '':
                        continue
                    try:
                        num = float(s.replace(',', ''))
                        formatted.append(f"{num:,.0f} $")
                    except Exception:
                        continue
            return 'Inconnu' if not formatted else '   ;   '.join(formatted)
        try:
            num = float(x)
            return f"{num:,.0f} $"
        except Exception:
            return 'Inconnu'

    def format_calc_df(self, df=None):
        """
        Formats and calculates additional fields in the DataFrame.
        Returns the formatted DataFrame (and updates internal df if df is None).
        """
        data = (self.df if df is None else df).copy()
        if data.empty:
            if df is None:
                self.df = data
            return data

        # Dates
        data['date_debut'] = pd.to_datetime(data['date_debut'], errors='coerce')
        data['date_fin'] = pd.to_datetime(data['date_fin'], errors='coerce')
        data = data.dropna(subset=['date_debut', 'date_fin']).sort_values('date_debut').reset_index(drop=True)
        data['duration_days'] = (data['date_fin'] - data['date_debut']).dt.days

        # Text fields
        if 'tender_title' in data.columns:
            data['tender_title'] = data['tender_title'].astype(str).str.slice(0, 50).fillna('') + '...'
        if 'seao_id' in data.columns:
            try:
                data['seao_id'] = data['seao_id'].astype(int).astype(str)
            except Exception:
                data['seao_id'] = data['seao_id'].astype(str)

        # option/opt normalization
        data['option'] = data.get('opt', pd.Series(0, index=data.index))
        data['opt'] = data['opt'].fillna('0')
        data['opt']= data['opt'].apply(lambda x: 0 if eval(x) <= 0 else 1)

        # index field
        def make_index(row):
            sid = str(row.get('seao_id', ''))
            lots = row.get('lots_name')
            if pd.notna(lots) and str(lots) != '':
                return (sid + '_' + str(lots))[:16]
            return sid[:16]
        data['index'] = data.apply(make_index, axis=1)

        # process options (duplicates)
        data = self.process_options(data)

        # option description
        data['option'] = data.apply(lambda row: row['pattern'] if row.get('pattern') == 'Base du contrat' else f"{row.get('pattern')} = {row.get('option')}", axis=1)

        # fill and clean other fields
        if 'lots_name' in data.columns:
            data['lots_name'] = data['lots_name'].fillna('-')
        data['date_fin'] = pd.to_datetime(data['date_fin']).dt.date
        data['DD'] = pd.to_datetime(data['date_debut']).dt.date
        data['DF'] = data['date_fin']

        if 'awards_suppliers_name' in data.columns:
            data['awards_suppliers_name'] = data['awards_suppliers_name'].fillna('Inconnu').astype(str)
            data['awards_suppliers_name'] = data['awards_suppliers_name'].str.replace("['", "", regex=False)
            data['awards_suppliers_name'] = data['awards_suppliers_name'].str.replace("']", "", regex=False)
            data['awards_suppliers_name'] = data['awards_suppliers_name'].str.replace("'", "", regex=False)
            data['awards_suppliers_name'] = data['awards_suppliers_name'].apply(lambda x: x[:150] + ' ... et plus' if len(x) > 150 else x)

        if 'awards_amount' in data.columns:
            data['awards_amount'] = data['awards_amount'].fillna(0)
            data['awards_amount'] = data['awards_amount'].apply(self.format_awards_amount)

        if df is None:
            self.df = data
        return data