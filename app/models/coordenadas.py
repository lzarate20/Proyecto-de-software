import math

from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import null
from app.db import db
from sqlalchemy import (
    cast,
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    text,
    select,
    and_,
    or_,
    Float,
)
from app.models.zonas_inundables import ZonaInundable
from app.models.recorridos_evacuacion import Recorridos


class Coordenadas(db.Model):
    """
    Coordenadas de las distintas zonas y recorridos del sistema

    Args:
        lat(string): coordenada latitud
        long(string): coordenada longitud
    """

    @classmethod
    def add_coords(cls, coords):
        """
        Se agregan las coordenadas al sistema, debe hacerse un update luego

        Args:
            coords(Coordenadas): coordenadas a agregar
        """
        db.session.add(coords)
        db.session.commit()

    @classmethod
    def get_or_create(cls, lat, long):
        """
        Creacion y retorno de las coordenadas pasadas por parámetro

        Args:
            lat, long (string): coordenadas
        """
        coords = Coordenadas.query.filter(
            (Coordenadas.lat == lat[:8]) & (Coordenadas.long == long[:8])
        ).first()
        if not coords:
            coords = Coordenadas(lat=lat, long=long)
            Coordenadas.add_coords(coords=coords)
        return coords

    __tablename__ = "coordenadas"
    id = Column(Integer, primary_key=True)
    lat = Column(String(255))
    long = Column(String(255))

    def __init__(self, lat, long):
        self.lat = round(lat, 8)
        self.long = round(long, 8)

    def get_by_id(id):
        """
        Retorna la coordenada con el id pasado por parámetro
        caso contrario None
        Args:
            id(int): id a buscar
        """
        return Coordenadas.query.filter(Coordenadas.id == id).first()

    def assign_zonas_inundables(self, zona, coords):
        """
        Se asignan las coordenadas de la zona

        Args:
            zona(Zona): zona inundable asociada
            coords(Coordenada): coordenada asociada a la zona
        """
        Coordenadas.add_coords(coords)
        self.zonasInundables.append(zona)
        db.session.commit()

    def assign_recorridos_evacuacion(self, recorrido, coords):
        """
        Se asignan las coordenadas del recorrido

        Args:
            recorrido(Recorrido): recorrido de evacuación asociado
            coords(Coordenada): coordenada asociada a la zona
        """
        Coordenadas.add_coords(coords)
        self.recorridosEvacuacion.append(recorrido)
        db.session.commit()

    def delete(self):
        """
        Se elimina la coordenada de la base de datos
        """
        db.session.delete(self)
        db.session.commit()

    def haversine(self, lat, lon):
        """Devuelve la distancia con otro punto
        :param lat(float):Numero real que representa la latitud
        :param lon(float):Numero real que representa la longitud"""

        rad = math.pi / 180
        dlat = lat - float(self.lat)
        dlon = lon - float(self.long)
        R = 6372.795477598
        a = (math.sin(rad * dlat / 2)) ** 2 + math.cos(
            rad * float(self.lat)
        ) * math.cos(rad * lat) * (math.sin(rad * dlon / 2)) ** 2
        distancia = 2 * R * math.asin(math.sqrt(a))
        return distancia
