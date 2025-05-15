from helper import hash_output
import pandas as pd
from sqlalchemy import create_engine, Integer, String, Float, Boolean, Column, ForeignKey, func, UniqueConstraint
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