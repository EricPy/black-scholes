from helper import hash_output, black_scholes_call, black_scholes_put
import pandas as pd
from sqlalchemy import create_engine, Integer, String, Float, Boolean, Column, ForeignKey, func, UniqueConstraint, desc
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

engine = create_engine('sqlite:///bsorm.db')

Base = declarative_base()

class BsInput(Base):
    __tablename__ = 'bsinputs'
    __table_args__ = (
        UniqueConstraint('input_hash', name='uix_input_hash'),
    )

    calc_id = Column(Integer, primary_key=True)
    stockp = Column(Float, nullable=False)
    strikep = Column(Float, nullable=False)
    interestr = Column(Float, nullable=False)
    vol = Column(Float, nullable=False)
    time = Column(Float, nullable=False)
    input_hash = Column(String, nullable=False)

    bsoutputs = relationship('BsOutput', back_populates='bsinput')

class BsOutput(Base):
    __tablename__ = 'bsoutputs'
    __table_args__ = (
        UniqueConstraint('output_hash', name='uix_output_hash'),
    )

    calcoutput_id = Column(Integer, primary_key=True)
    vol_shock = Column(Float, nullable=True) # Stores the increment from the base volatility input
    stockp_shock = Column(Float, nullable=True) # Stores the increment from the base stock price input
    optionp = Column(Float, nullable=True)
    iscall = Column(Boolean, nullable=True)
    calc_id = Column(Integer, ForeignKey('bsinputs.calc_id'))
    output_hash = Column(String, nullable=False)

    bsinput = relationship('BsInput', back_populates='bsoutputs')

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

# Function to save inputs
def save_input(input_hash, session, input_data: pd.DataFrame):
    input_row = input_data.iloc[0]

    existing = session.query(BsInput).filter_by(input_hash=input_hash).first()
    if existing:
        return existing.calc_id

    bsinput = BsInput(
        stockp=input_row["stockp"],
        strikep=input_row["strikep"],
        interestr=input_row["interestr"],
        vol=input_row["vol"],
        time=input_row["time"],
        input_hash=input_hash
    )

    session.add(bsinput)
    session.flush()

    return bsinput.calc_id

# Function to save outputs
def save_output(session, output_df: pd.DataFrame, iscall: bool, base_vol, base_stockp, input_id):
    """
    Stores the result of the shock test heatmap in the bsoutputs database
    """

    for index, row in output_df.iterrows():        
        for stock_price in row.index:
            # Check if the output is unique
            output_data = {
                "vol_shock": round((index - base_vol), 2), # The change / shock in volume from the base input
                "stockp_shock": round((stock_price - base_stockp), 2), # The change / shock in stock price from the base input
                "optionp": round(row[stock_price], 2),
                "iscall": iscall,
                "calc_id": input_id
            }

            # Check the hash
            output_hash = hash_output(**output_data)
            existing = session.query(BsOutput).filter_by(output_hash=output_hash).first()
            if existing:
                continue

            bsoutput = BsOutput(
                vol_shock=output_data["vol_shock"],
                stockp_shock=output_data["stockp_shock"],
                optionp=output_data["optionp"],
                iscall=iscall,
                calc_id=input_id,
                output_hash=output_hash
            )

            session.add(bsoutput)

# Function to save the base black-scholes output
def save_single_output(session, vol, stockp, optionp, iscall, calc_id, base_vol, base_stockp):
    # Check if the output is unique
    output_data = {
        "vol_shock": round((vol - base_vol), 2), # The change / shock in volume from the base input
        "stockp_shock": round((stockp - base_stockp), 2), # The change / shock in stock price from the base input
        "optionp": round(optionp, 2),
        "iscall": iscall,
        "calc_id": calc_id
    }

    # Check the hash
    output_hash = hash_output(**output_data)
    existing = session.query(BsOutput).filter_by(output_hash=output_hash).first()
    if not existing:
        bsoutput = BsOutput(
            vol_shock=output_data["vol_shock"],
            stockp_shock=output_data["stockp_shock"],
            optionp=output_data["optionp"],
            iscall=iscall,
            calc_id=calc_id,
            output_hash=output_hash
        )

        session.add(bsoutput)
        return True
    else:
        print("Entry already exists, not saved again.")
        return False
    
# Function that outputs the most recent entries as pandas dataframe
def show_recent(session, number_of_entries):
    """
    Grab N latest entries into outputs
    and return a dataframe with the relevant data
    """

    # Grab the most recent entries into the SQL database
    half = number_of_entries // 2

    recent_entries_call = (
        session.query(BsOutput, BsInput)
        .join(BsInput, BsOutput.calc_id == BsInput.calc_id)
        .filter(BsOutput.iscall == True)
        .order_by(BsOutput.calcoutput_id.desc())
        .limit(half)
        .all()
    )

    recent_entries_put = (
        session.query(BsOutput, BsInput)
        .join(BsInput, BsOutput.calc_id == BsInput.calc_id)
        .filter(BsOutput.iscall == False)
        .order_by(BsOutput.calcoutput_id.desc())
        .limit(half)
        .all()
    )

    combined_result = recent_entries_call + recent_entries_put

    # Create dataframe with the relevant data
    result_df = []

    for output, input_ in combined_result:
        
        # Calculate Base Option Value
        if output.iscall:
            base_value = black_scholes_call(input_.stockp, input_.strikep, input_.time, input_.interestr, input_.vol)
        else:
            base_value = black_scholes_put(input_.stockp, input_.strikep, input_.time, input_.interestr, input_.vol)

        # Formatting for clarity
        option_type = "Call" if output.iscall else "Put"
        volume_shock = f"+ {output.vol_shock}" if output.vol_shock > 0 else f"{output.vol_shock}"
        price_shock = f"+ {output.stockp_shock}" if output.stockp_shock > 0 else f"{output.stockp_shock}"
        
        row = {
            "Type": option_type,
            "Rf": input_.interestr,
            "TTM": input_.time,
            "Strike": input_.strikep,
            "Base Vol.": input_.vol,
            "Base Spot Price": input_.stockp,
            "Shock Vol.": volume_shock,
            "Shock Spot Price": price_shock,
            "Base Option Value": round(base_value, 2),
            "Shocked Option Value": round(output.optionp, 2)
        }

        result_df.append(row)

    return pd.DataFrame(result_df)