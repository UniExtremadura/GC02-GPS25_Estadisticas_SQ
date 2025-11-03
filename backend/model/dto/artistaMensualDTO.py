from sqlalchemy import Column, Integer, BigInteger, CheckConstraint
from model.factory.model import Base

class ArtistaMensual(Base):
    __tablename__ = "artistasMensual"

    idArtista = Column(Integer, primary_key=True, index=True)
    numOyentes = Column(BigInteger, default=0, nullable=False)
    numSeguidores = Column(BigInteger, default=0, nullable=False)

    __table_args__ = (
        CheckConstraint("numOyentes >= 0"),
        CheckConstraint("numSeguidores >= 0"),
    )
