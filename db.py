from sqlalchemy import create_engine, Integer, String, Float, Boolean, Column, ForeignKey, func
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

engine = create_engine('sqlite:///bsorm.db')

Base = declarative_base()

class BsInput(Base):
    __tablename__ = 'bsinputs'
    calc_id = Column(Integer, primary_key=True)
    stockp = Column(Float, nullable=False)
    strikep = Column(Float, nullable=False)
    interestr = Column(Float, nullable=False)
    vol = Column(Float, nullable=False)
    time = Column(Float, nullable=False)

    bsoutputs = relationship('BsOutput', back_populates='bsinput')


class BsOutput(Base):
    __tablename__ = 'bsoutputs'
    calcoutput_id = Column(Integer, primary_key=True)
    vol_shock = Column(Float, nullable=True) # Stores the increment from the base volatility input
    stockp_shock = Column(Float, nullable=True) # Store the increment from the base stock price input
    optionp = Column(Float, nullable=True)
    iscall = Column(Boolean, nullable=True)
    calc_id = Column(Integer, ForeignKey('bsinputs.calc_id'))

    bsinput = relationship('BsInput', back_populates='bsoutputs')

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()