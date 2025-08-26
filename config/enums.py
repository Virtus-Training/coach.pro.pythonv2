from __future__ import annotations

"""Enumerations and label mappings for exercises."""

from enum import Enum


class PrimaryMuscle(Enum):
    PECTORAUX = "Pectoraux"
    DORSAUX = "Dorsaux"
    EPAULES = "Épaules"
    BICEPS = "Biceps"
    TRICEPS = "Triceps"
    TRAPEZES = "Trapèzes"
    LOMBAIRES = "Lombaires"
    ABDOMINAUX = "Abdominaux"
    OBLIQUES = "Obliques"
    QUADRICEPS = "Quadriceps"
    ISCHIO_JAMBIERS = "Ischio-jambiers"
    FESSIERS = "Fessiers"
    MOLLETS = "Mollets"
    AVANT_BRAS = "Avant-bras"
    COU = "Cou"
    CORPS_ENTIER = "Corps entier"


class Equipment(Enum):
    BAR = "Barre"
    DB = "Haltères"
    KB = "Kettlebell"
    CBL = "Poulie/Câble"
    MACH = "Machine guidée"
    SMITH = "Smith"
    BAND = "Élastiques"
    TRX = "TRX/Anneaux"
    BW = "Poids du corps"
    BENCH = "Banc/Step/Box"
    SBALL = "Swiss Ball"
    MBALL = "Médecine ball"
    SLED = "Sled/Prowler"


class MovementPattern(Enum):
    SQUAT = "Squat"
    HINGE = "Hinge"
    LUNGE = "Fente"
    PH = "Push horizontal"
    PV = "Push vertical"
    RH = "Tirage horizontal"
    RV = "Tirage vertical"
    CORE_AEXT = "Gainage"
    CORE_AROT = "Anti-rotation"
    CORE_ROT = "Rotation"
    LOCO = "Locomotion/Carry"
    PLYO = "Saut/Pliométrie"
    COND = "Conditioning"
    MOB = "Mobilité"


PRIMARY_MUSCLE_LABELS = {e.name: e.value for e in PrimaryMuscle}
PRIMARY_MUSCLE_CODES = {e.value: e.name for e in PrimaryMuscle}

EQUIPMENT_LABELS = {e.name: e.value for e in Equipment}
EQUIPMENT_CODES = {e.value: e.name for e in Equipment}

PATTERN_LABELS = {e.name: e.value for e in MovementPattern}
PATTERN_CODES = {e.value: e.name for e in MovementPattern}


__all__ = [
    "PrimaryMuscle",
    "Equipment",
    "MovementPattern",
    "PRIMARY_MUSCLE_LABELS",
    "PRIMARY_MUSCLE_CODES",
    "EQUIPMENT_LABELS",
    "EQUIPMENT_CODES",
    "PATTERN_LABELS",
    "PATTERN_CODES",
]

