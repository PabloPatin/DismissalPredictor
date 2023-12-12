from sqlalchemy import create_engine, Column, Integer, ARRAY, VARCHAR, ForeignKey, TIMESTAMP, Text, Boolean, inspect, \
    select
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine('postgresql://postgres:password@localhost:5432/db', client_encoding='utf8')

session = sessionmaker(bind=engine)()

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)

    def __repr__(self):
        return f"<{__class__.__name__}(id={self.id})>"


class Employee(BaseModel):
    __tablename__ = 'employees'

    name = Column(VARCHAR(255), nullable=False)
    position = Column(VARCHAR(255), nullable=False)
    email = Column(VARCHAR(255), unique=True, nullable=False)

    @staticmethod
    def get_all_employee():
        return session.query(Employee).all()

    # TODO: продумать реализацию и доделать методы
    @staticmethod
    def add_employee(name_or_employee, position='', email=''):
        employee = name_or_employee if isinstance(name_or_employee, Employee) \
            else Employee(name_or_employee, position, email)
        try:
            session.add(employee)
            session.commit()
        except Exception as ex:
            print("Ошибка -", ex)
            session.rollback()

    @staticmethod
    def get_employee_by_id(id):
        return session.query(Employee).get(id)

    @staticmethod
    def get_employee_by_email(email):
        return session.query(Employee).filter_by(email=email).first()


class Dismissal(BaseModel):
    __tablename__ = 'dismissals'

    employee_id = Column(Integer, ForeignKey('employees.id', ondelete='CASCADE'), nullable=False, index=True)
    date = Column(TIMESTAMP, nullable=False)


class Message(BaseModel):
    __tablename__ = 'messages'

    employee_id = Column(Integer, ForeignKey('employees.id', ondelete='CASCADE'), nullable=False, index=True)
    send_date = Column(TIMESTAMP, nullable=False)
    sender = Column(VARCHAR(255), nullable=False)
    receiver = Column(VARCHAR(255), nullable=False)
    text = Column(Text, nullable=True)
    copy = Column(ARRAY(Text), nullable=True)
    hidden_copy = Column(ARRAY(Text), nullable=True)
    read_time = Column(TIMESTAMP, nullable=True)
    have_answer = Column(Boolean)


def main():
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    main()

