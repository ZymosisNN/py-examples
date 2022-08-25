import sqlalchemy as sa
from sqlalchemy.orm import relationship
from base import Base, session, create_db, Session, engine
from logger import log


ass = sa.Table(
    'ass', Base.metadata,
    sa.Column('human_id', sa.Integer, sa.ForeignKey('human.id'), nullable=False, primary_key=True),
    sa.Column('shop_id', sa.Integer, sa.ForeignKey('shop.id'), nullable=False, primary_key=True)
)


class Blood(Base):
    __tablename__ = 'blood'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    title = sa.Column(sa.String(30))

    human_refs = relationship('Human', back_populates='blood_ref')

    def __repr__(self):
        return f'Blood({self.title} {self.human_refs})'


class Passport(Base):
    __tablename__ = 'passport'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    timestamp = sa.Column(sa.String(40))
    human_ref = relationship('Human', back_populates='passport_ref', uselist=False)

    def __repr__(self):
        return f'Passport({self.id})'


class Shop(Base):
    __tablename__ = 'shop'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    human_refs = relationship('Human', secondary=ass, back_populates='shop_refs', lazy=True)

    def __repr__(self):
        return f'Shop({self.id}, {self.human_refs})'


class Human(Base):
    __tablename__ = 'human'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(50))
    passport_id = sa.Column(sa.Integer, sa.ForeignKey(Passport.id), nullable=False)
    blood_id = sa.Column(sa.Integer, sa.ForeignKey(Blood.id), nullable=False)

    blood_ref = relationship('Blood', back_populates='human_refs')                           # one -- many
    passport_ref = relationship('Passport', back_populates='human_ref', uselist=False)       # one -- one
    shop_refs = relationship('Shop', secondary=ass, back_populates='human_refs', lazy=True)  # many -- many

    def __repr__(self):
        return f'Human({self.name})'


def test():
    with session() as s:
        human = s.query(Human).first()
        passport = s.query(Passport).first()

        log.info(human)
        ppp = human.passport_ref
        log.info(ppp)
        log.info(passport)
        log.info(passport is ppp)
        log.info(passport == ppp)
        log.info(passport.human_ref)
        log.info(passport.human_ref == human)

        # log.info(h.blood_ref)
        # log.info(type(h.blood_ref))


def fill_human():
    with session() as s:
        # shops = Shop(), Shop(), Shop()
        # for shop in shops:
        #     s.add(shop)

        # s.add(Passport(timestamp='2021 January'))
        # s.add(Passport(timestamp='2021 February'))
        # s.add(Passport(timestamp='2021 March'))

        # h = Human(name='Medved', passport_id=1, blood_id=1)
        # h.shop_refs.append(shops[0])
        # h.shop_refs.append(shops[1])
        # h.shop_refs.append(shops[2])
        # s.add(h)
        # h = Human(name='Lisa', passport_id=2, blood_id=1)
        # h.shop_refs.extend(shops[1:3])
        # s.add(h)

        s.add(Human(name='Olen', passport_id=1, blood_id=1))


if __name__ == '__main__':
    # create_db()
    # fill_human()
    test()
    # s = Session(bind=engine)
