def procesar(segmentos, reqs, marcos_libres):
    PAGE_SIZE = 32
    tabla_paginas = {}  # clave: (segmento, página relativa) -> marco físico
    cola_fifo = []
    resultados = []
    pasos_paginas = []

    def buscar_segmento(dir_virtual):
        for nombre, base, limite in segmentos:
            if base <= dir_virtual < base + limite:
                return nombre, base
        return None, None

    for req in reqs:
        segmento, base = buscar_segmento(req)
        if segmento is None:
            resultados.append((req, 0x1FF, "Segmention Fault"))
            pasos_paginas.append(cola_fifo.copy())
            continue

        desplazamiento = req - base
        pagina_relativa = desplazamiento // PAGE_SIZE
        clave_pagina = (segmento, pagina_relativa)

        if clave_pagina in tabla_paginas:
            marco = tabla_paginas[clave_pagina]
            direccion_fisica = marco * PAGE_SIZE + (req % PAGE_SIZE)
            resultados.append((req, direccion_fisica, "Marco ya estaba asignado"))
        else:
            if marcos_libres:
                nuevo_marco = marcos_libres.pop(0)
                tabla_paginas[clave_pagina] = nuevo_marco
                cola_fifo.append(clave_pagina)
                direccion_fisica = nuevo_marco * PAGE_SIZE + (req % PAGE_SIZE)
                resultados.append((req, direccion_fisica, "Marco libre asignado"))
            else:
                pagina_removida = cola_fifo.pop(0)
                marco_reemplazo = tabla_paginas[pagina_removida]
                del tabla_paginas[pagina_removida]
                tabla_paginas[clave_pagina] = marco_reemplazo
                cola_fifo.append(clave_pagina)
                direccion_fisica = marco_reemplazo * PAGE_SIZE + (req % PAGE_SIZE)
                resultados.append((req, direccion_fisica, "Marco asignado"))

        pasos_paginas.append(cola_fifo.copy())

    return resultados, pasos_paginas



def print_results(results):
    for i, (req, dir_fis, accion) in enumerate(results):
        print(f"Req: {req:#04x} Direccion Fisica: {dir_fis:#04x} Acción: {accion}")


def print_pasos(pasos_paginas):
    print("\nEvolución de páginas cargadas en los marcos (FIFO):")
    for i, estado in enumerate(pasos_paginas):
        print(f"Paso {i + 1}: {estado}")


if __name__ == '__main__':
    marcos_libres = [0x1, 0x0, 0x2]

    reqs = [0x00, 0x12, 0x64, 0x65, 0x8D, 0x8F, 0x19, 0x18, 0xF1, 0x0B, 0xDF, 0x0A]

    segmentos = [
        ('.text', 0x00, 0x1A),
        ('.data', 0x40, 0x28),
        ('.heap', 0x80, 0x1F),
        ('.stack', 0xC0, 0x22),
    ]

    resultados, pasos = procesar(segmentos, reqs, marcos_libres)
    print_results(resultados)
    print_pasos(pasos)
