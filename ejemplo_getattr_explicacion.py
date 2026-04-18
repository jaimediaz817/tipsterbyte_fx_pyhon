"""
✅ EJEMPLO BASICO Y EXACTO DE COMO FUNCIONA __getattr__
Este es el truco mas poderoso que existe para refactors graduales.
Es el que nos permitio cambiar TODO sin romper NADA.
"""


class RepositorioNuevo:
    """✅ Esta es la interfaz nueva y chica (ISP)"""

    def get_usuario(self):
        return "Usuario desde repositorio nuevo"

    def get_producto(self):
        return "Producto desde repositorio nuevo"


class RepositorioViejo(RepositorioNuevo):
    """❌ Esta es la interfaz vieja y gigante que queremos eliminar"""

    def __getattr__(self, nombre_metodo: str):
        """
        ✅ MAGIA AQUI:
        Este metodo SOLO se ejecuta CUANDO NO EXISTE el metodo en esta clase.

        Como esta clase hereda de RepositorioNuevo, TODOS los metodos ya existen aqui.
        Asi que este metodo NUNCA se ejecuta en codigo nuevo.

        SOLO se ejecuta cuando alguien usa la interfaz vieja.
        """
        print(f"\n⚠️  WARNING: Alguien esta usando el metodo '{nombre_metodo}'")
        print("⚠️  Usa la interfaz nueva en su lugar")

        # ✅ Y lo mejor de todo: devolvemos el metodo igual para que siga funcionando
        return getattr(super(), nombre_metodo)


# ✅ CASO 1: CODIGO NUEVO (BIEN)
print("✅ CASO 1: Codigo nuevo usando la interfaz correcta:")
repo_bueno = RepositorioNuevo()
print(repo_bueno.get_usuario())
# ✅ NO HAY WARNING. NADA SE EJECUTA DE MAS. CERO COSTE.


# ✅ CASO 2: CODIGO VIEJO (MAL PERO SIGUE FUNCIONANDO)
print("\n\n✅ CASO 2: Codigo viejo que aun usa la interfaz mala:")
repo_malo = RepositorioViejo()
print(repo_malo.get_usuario())
# ✅ SIGUE FUNCIONANDO EXACTAMENTE IGUAL
# ✅ Pero ahora le sale un warning avisandole que cambie


# ✅ ESTO ES LO QUE LOGRAMOS NOSOTROS:
#
# 🔹 1. Todo el codigo nuevo usa las interfaces chicas ✅
# 🔹 2. Todo el codigo viejo sigue funcionando EXACTAMENTE igual ✅
# 🔹 3. Nadie se da cuenta de que estamos cambiando nada ✅
# 🔹 4. Podemos migrar un archivo cada dia sin prisas ✅
# 🔹 5. Nunca tenemos un momento en que el codigo este roto ✅
# 🔹 6. Podemos parar en cualquier momento y volver atras ✅
#
# ❌ ESTO ES LO QUE HACEN TODOS LOS DEMAS:
# Cambian todo de golpe, rompen todo, trabajan 12 horas seguidas,
# tienen que deshacer todo al final y nadie entiende nada.
#
# ✅ ESTO ES CLEAN ARCHITECTURE DE VERDAD.
