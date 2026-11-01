# Base de conocimiento: sistema experto de diagnóstico de fallas en vivienda

7 categorías, 36 preguntas (síntomas) y 49 reglas If / And / Then. Cada pregunta se responde Sí o No.

## Categoría ELE · Eléctrica

Preguntas:
- `olor_quemado`: ¿Olor a quemado en tomas o tablero?
- `sobrecalentamiento`: ¿Enchufes o interruptores sobrecalentados?
- `breaker`: ¿El breaker se dispara con frecuencia?
- `chispas`: ¿Chispas al conectar un electrodoméstico?
- `cables`: ¿Cables expuestos o deteriorados?
- `cortos`: ¿Cortocircuitos frecuentes?
- `parpadeo`: ¿Parpadeo constante de las luces?
- `tomas`: ¿Tomas que dejan de funcionar?

Reglas:
- **E01** (Alta, FC 88 %): If olor_quemado = Sí And sobrecalentamiento = No And breaker = Sí Then **Sobrecarga del circuito o falla en el tablero**. Especialista: Electricista certificado. Acción: Bajar el breaker de la zona afectada y no volver a usarla hasta la revisión de un electricista.
- **E02** (Critica, FC 92 %): If olor_quemado = No And chispas = Sí And cables = Sí Then **Riesgo de cortocircuito**. Especialista: Electricista (atención urgente). Acción: Desconectar el electrodoméstico afectado y no usar esa toma ni los cables expuestos hasta la revisión.
- **E03** (Media, FC 72 %): If olor_quemado = No And chispas = No And cables = No And cortos = No And sobrecalentamiento = No And parpadeo = Sí Then **Fluctuación de voltaje o falla de conexión**. Especialista: Electricista. Acción: Evitar conectar electrodomésticos sensibles hasta confirmar la causa de la fluctuación.
- **E04** (Baja, FC 75 %): If olor_quemado = No And chispas = No And cables = No And cortos = No And sobrecalentamiento = No And parpadeo = No And breaker = No And tomas = Sí Then **Fallo puntual en toma de corriente**. Especialista: Electricista (revisión programada). Acción: Probar la toma con otro electrodoméstico y, si el problema persiste, programar una revisión de rutina.
- **E05** (Critica, FC 93 %): If olor_quemado = Sí And sobrecalentamiento = Sí Then **Riesgo de incendio eléctrico**. Especialista: Electricista (atención urgente). Acción: Bajar el breaker de inmediato, no volver a energizar la zona y llamar a un electricista con carácter urgente.
- **E06** (Alta, FC 85 %): If olor_quemado = No And chispas = No And cables = No And cortos = Sí And breaker = Sí Then **Corto en la instalación**. Especialista: Electricista. Acción: Evitar reactivar el breaker repetidamente y solicitar revisión de la instalación antes de seguir usando el circuito.
- **E07** (Media, FC 78 %): If olor_quemado = No And chispas = No And cables = Sí Then **Deterioro de la instalación eléctrica**. Especialista: Electricista. Acción: Evitar el contacto con los cables expuestos y aislar temporalmente la zona mientras se programa la reparación.
- **E08** (Alta, FC 76 %): If olor_quemado = Sí And sobrecalentamiento = No And breaker = No Then **Conexión floja o punto caliente en toma o tablero**. Especialista: Electricista. Acción: Desconectar los equipos de la toma afectada, bajar el breaker de la zona si el olor persiste y solicitar revisión.
- **E09** (Alta, FC 78 %): If olor_quemado = No And chispas = Sí And cables = No Then **Desgaste de contactos en la toma o la clavija**. Especialista: Electricista. Acción: No volver a usar la toma ni el enchufe que produjo la chispa hasta que sean revisados.
- **E10** (Alta, FC 70 %): If olor_quemado = No And chispas = No And cables = No And cortos = Sí And breaker = No Then **Protección del circuito deficiente**. Especialista: Electricista certificado. Acción: Limitar el uso del circuito afectado y solicitar la revisión del tablero y de sus protecciones.
- **E11** (Media, FC 72 %): If olor_quemado = No And chispas = No And cables = No And cortos = No And sobrecalentamiento = No And parpadeo = No And breaker = Sí Then **Sobrecarga por uso simultáneo de equipos**. Especialista: Electricista. Acción: Repartir los equipos de alto consumo entre distintos circuitos y evitar usarlos al mismo tiempo hasta la revisión.
- **E12** (Alta, FC 77 %): If olor_quemado = No And chispas = No And cables = No And cortos = No And sobrecalentamiento = Sí Then **Conexión deficiente o sobrecarga en enchufe o interruptor**. Especialista: Electricista. Acción: Desconectar los equipos del punto sobrecalentado y no volver a usarlo hasta que sea revisado.

## Categoría HID · Hidráulica

Preguntas:
- `fuga_visible`: ¿Fuga visible en tuberías?
- `humedad_lavamanos`: ¿Humedad bajo el lavamanos?
- `agua_color`: ¿Agua con color o turbidez?
- `mal_olor_desague`: ¿Mal olor en los desagües?
- `obstruccion`: ¿Desagües obstruidos o lentos?
- `baja_presion`: ¿Baja presión de agua?
- `golpeteo`: ¿Golpeteo en las tuberías?
- `goteo`: ¿Goteo constante en grifos?

Reglas:
- **H01** (Alta, FC 90 %): If fuga_visible = Sí And humedad_lavamanos = Sí Then **Fuga activa en tubería de suministro**. Especialista: Plomero. Acción: Cerrar la llave de paso de esa zona para detener la fuga mientras llega el plomero.
- **H02** (Media, FC 68 %): If fuga_visible = No And agua_color = No And humedad_lavamanos = No And obstruccion = No And baja_presion = Sí Then **Obstrucción parcial o sedimentación**. Especialista: Plomero. Acción: Evitar el uso simultáneo de varias salidas de agua mientras se programa la revisión.
- **H03** (Baja, FC 70 %): If fuga_visible = No And agua_color = No And humedad_lavamanos = No And obstruccion = No And baja_presion = No And golpeteo = Sí Then **Golpe de ariete o aire atrapado**. Especialista: Plomero. Acción: Cerrar las llaves de forma gradual mientras se programa la revisión; no representa una urgencia.
- **H04** (Media, FC 82 %): If fuga_visible = No And agua_color = No And humedad_lavamanos = No And obstruccion = Sí And mal_olor_desague = Sí Then **Taponamiento en la red de desagüe**. Especialista: Plomero. Acción: Evitar verter más agua o residuos por ese desagüe hasta destaparlo o hacerlo revisar.
- **H05** (Baja, FC 74 %): If fuga_visible = No And agua_color = No And humedad_lavamanos = No And obstruccion = No And baja_presion = No And golpeteo = No And goteo = Sí Then **Empaque o válvula desgastada**. Especialista: Plomero. Acción: Cerrar bien la llave tras cada uso y programar el cambio del empaque; no es urgente.
- **H06** (Alta, FC 80 %): If fuga_visible = No And agua_color = Sí Then **Contaminación o corrosión en la tubería**. Especialista: Plomero / empresa de acueducto. Acción: Suspender el consumo de esa agua para bebida o cocina hasta que sea evaluada.
- **H07** (Media, FC 76 %): If fuga_visible = No And agua_color = No And humedad_lavamanos = Sí And mal_olor_desague = Sí Then **Fuga oculta en conexión de desagüe**. Especialista: Plomero. Acción: Revisar la conexión bajo el mueble y evitar el uso intensivo de esa salida hasta la revisión.
- **H08** (Media, FC 80 %): If fuga_visible = Sí And humedad_lavamanos = No Then **Fuga localizada en conexión o accesorio**. Especialista: Plomero. Acción: Cerrar la llave de paso de la zona y colocar un recipiente bajo la fuga mientras llega el plomero.
- **H09** (Media, FC 70 %): If fuga_visible = No And agua_color = No And humedad_lavamanos = Sí And mal_olor_desague = No Then **Filtración en conexión de suministro bajo el mueble**. Especialista: Plomero. Acción: Secar la zona, revisar las mangueras de abasto y vigilar si la mancha crece.
- **H10** (Baja, FC 75 %): If fuga_visible = No And agua_color = No And humedad_lavamanos = No And obstruccion = Sí And mal_olor_desague = No Then **Obstrucción localizada en sifón o desagüe**. Especialista: Plomero. Acción: Limpiar el sifón o usar un destapador manual, sin mezclar productos químicos; si persiste, llamar al plomero.
- **H11** (Baja, FC 72 %): If fuga_visible = No And agua_color = No And humedad_lavamanos = No And obstruccion = No And baja_presion = No And golpeteo = No And goteo = No And mal_olor_desague = Sí Then **Sifón seco o ventilación deficiente del desagüe**. Especialista: Plomero. Acción: Dejar correr agua en los desagües poco usados para restablecer el sello del sifón; si el olor persiste, solicitar revisión.

## Categoría EST · Estructural

Preguntas:
- `hundimiento`: ¿Hundimiento o desnivel en el piso?
- `inclinacion`: ¿Inclinación en muros o columnas?
- `grietas_diagonales`: ¿Grietas diagonales en paredes?
- `puertas`: ¿Puertas o ventanas que no cierran?
- `grietas_vh`: ¿Grietas verticales u horizontales?
- `humedad_ascendente`: ¿Humedad ascendente en muros?
- `fisuras_techo`: ¿Fisuras finas en el techo?
- `panete`: ¿Desprendimiento de pañete?

Reglas:
- **S01** (Alta, FC 85 %): If hundimiento = No And grietas_diagonales = Sí And puertas = Sí Then **Asentamiento diferencial de la estructura**. Especialista: Ingeniero civil. Acción: Evitar sobrecargar la zona afectada y contactar a un ingeniero civil para una evaluación estructural pronta.
- **S02** (Baja, FC 70 %): If hundimiento = No And grietas_diagonales = No And inclinacion = No And grietas_vh = No And humedad_ascendente = No And fisuras_techo = Sí Then **Fisuras superficiales por contracción**. Especialista: Maestro de obra. Acción: Monitorear la fisura periódicamente; no requiere atención inmediata si no crece ni se acompaña de otros síntomas.
- **S03** (Critica, FC 92 %): If hundimiento = Sí And inclinacion = Sí Then **Riesgo de falla en la cimentación**. Especialista: Ingeniero civil (atención urgente). Acción: Restringir el acceso a la zona afectada y contactar de inmediato a un ingeniero civil.
- **S04** (Media, FC 73 %): If hundimiento = No And grietas_diagonales = No And inclinacion = No And grietas_vh = No And humedad_ascendente = Sí Then **Humedad capilar en cimientos**. Especialista: Ingeniero civil / impermeabilizador. Acción: Evitar revestir la zona húmeda hasta aplicar una solución de impermeabilización.
- **S05** (Baja, FC 72 %): If hundimiento = No And grietas_diagonales = No And inclinacion = No And grietas_vh = No And humedad_ascendente = No And fisuras_techo = No And panete = Sí Then **Deterioro superficial del recubrimiento**. Especialista: Maestro de obra. Acción: Retirar el material suelto para evitar caídas y programar el resane; no representa riesgo estructural.
- **S06** (Alta, FC 80 %): If hundimiento = No And grietas_diagonales = No And inclinacion = Sí Then **Desplome estructural incipiente**. Especialista: Ingeniero civil. Acción: Evitar permanecer cerca del muro inclinado y solicitar una evaluación estructural con prontitud.
- **S07** (Alta, FC 80 %): If hundimiento = Sí And inclinacion = No Then **Asentamiento del piso o falla del contrapiso**. Especialista: Ingeniero civil. Acción: Evitar ubicar cargas pesadas sobre la zona hundida y solicitar la evaluación de un ingeniero civil.
- **S08** (Media, FC 74 %): If hundimiento = No And grietas_diagonales = Sí And puertas = No Then **Grietas por movimiento estructural localizado**. Especialista: Ingeniero civil. Acción: Marcar los extremos de la grieta con la fecha para vigilar si crece y programar una evaluación estructural.
- **S09** (Media, FC 70 %): If hundimiento = No And grietas_diagonales = No And inclinacion = No And grietas_vh = Sí Then **Fisuración de muros por retracción o cargas**. Especialista: Ingeniero civil. Acción: Registrar con fotografías la ubicación y la longitud de la grieta, y solicitar una revisión si aumenta.
- **S10** (Baja, FC 68 %): If hundimiento = No And grietas_diagonales = No And inclinacion = No And grietas_vh = No And humedad_ascendente = No And fisuras_techo = No And panete = No And puertas = Sí Then **Desajuste de la carpintería de puertas o ventanas**. Especialista: Técnico en carpintería. Acción: Revisar bisagras y herrajes; si el problema aparece junto con grietas, repetir el diagnóstico estructural.

## Categoría HUM · Humedad

Preguntas:
- `manchas`: ¿Manchas de humedad en techo o pared?
- `moho`: ¿Moho u hongos visibles?
- `pintura`: ¿Pintura descascarada o ampollada?
- `olor_humedad`: ¿Olor persistente a humedad?
- `condensacion`: ¿Condensación en ventanas?

Reglas:
- **M01** (Alta, FC 83 %): If manchas = Sí And moho = Sí Then **Filtración activa desde la cubierta**. Especialista: Impermeabilizador / ingeniero civil. Acción: Proteger los objetos bajo la zona afectada y contactar a un impermeabilizador con prontitud.
- **M02** (Media, FC 75 %): If manchas = No And moho = No And pintura = Sí And olor_humedad = Sí Then **Humedad acumulada bajo el recubrimiento**. Especialista: Impermeabilizador. Acción: Ventilar el espacio y evitar sellar la zona con pintura nueva hasta resolver la humedad de fondo.
- **M03** (Baja, FC 68 %): If manchas = No And moho = No And pintura = No And condensacion = Sí Then **Ventilación insuficiente o puente térmico**. Especialista: Revisión de ventilación. Acción: Ventilar el espacio con regularidad y secar la condensación para evitar la aparición de moho.
- **M04** (Media, FC 71 %): If manchas = No And moho = Sí Then **Humedad ambiental elevada**. Especialista: Revisión de ventilación / impermeabilizador. Acción: Mejorar la ventilación de la zona y limpiar el moho visible con los productos adecuados.
- **M05** (Media, FC 74 %): If manchas = Sí And moho = No Then **Filtración incipiente o fuga en tubería empotrada**. Especialista: Plomero / impermeabilizador. Acción: Delimitar la mancha con lápiz y observar si crece; verificar si coincide con tuberías o con días de lluvia.
- **M06** (Baja, FC 65 %): If manchas = No And moho = No And pintura = Sí And olor_humedad = No Then **Deterioro del acabado por humedad residual**. Especialista: Maestro de obra / pintor. Acción: Raspar la pintura suelta, dejar secar el muro y aplicar un sellador antes de volver a pintar.
- **M07** (Baja, FC 66 %): If manchas = No And moho = No And pintura = No And condensacion = No And olor_humedad = Sí Then **Humedad oculta o ventilación insuficiente**. Especialista: Revisión de ventilación. Acción: Ventilar el espacio a diario y revisar zonas cerradas (clósets, detrás de muebles) en busca de humedad.

## Categoría GAS · Gas

Preguntas:
- `olor_gas`: ¿Olor característico a gas?
- `silbido`: ¿Silbido en tuberías de gas?
- `consumo_gas`: ¿Consumo de gas inusualmente alto?
- `llama_amarilla`: ¿Llama amarilla o naranja?

Reglas:
- **G01** (Critica, FC 95 %): If olor_gas = Sí And silbido = Sí Then **Fuga activa de gas**. Especialista: Empresa de gas (atención urgente). Acción: Ventilar de inmediato, no accionar interruptores ni encender llamas, y llamar a la empresa de gas desde afuera.
- **G02** (Media, FC 78 %): If olor_gas = No And silbido = No And consumo_gas = No And llama_amarilla = Sí Then **Combustión incompleta o quemador desajustado**. Especialista: Técnico de gas. Acción: Apagar la estufa y no usarla hasta que un técnico de gas revise y ajuste el quemador.
- **G03** (Alta, FC 74 %): If olor_gas = No And silbido = No And consumo_gas = Sí Then **Posible fuga menor no perceptible**. Especialista: Técnico de gas. Acción: Revisar visualmente las conexiones y solicitar una revisión técnica próxima, aunque no haya olor perceptible.
- **G04** (Critica, FC 82 %): If olor_gas = Sí And silbido = No Then **Fuga leve de gas**. Especialista: Empresa de gas (atención urgente). Acción: Ventilar de inmediato, no accionar interruptores ni encender llamas, cerrar la llave de paso del gas y llamar a la empresa de gas desde afuera.
- **G05** (Critica, FC 88 %): If olor_gas = No And silbido = Sí And consumo_gas = Sí Then **Fuga en conexión no detectada por el olfato**. Especialista: Empresa de gas (atención urgente). Acción: Ventilar de inmediato y contactar a la empresa de gas con carácter urgente, aunque no se perciba olor.
- **G06** (Critica, FC 80 %): If olor_gas = No And silbido = Sí And consumo_gas = No Then **Posible fuga en conexión de gas**. Especialista: Empresa de gas (atención urgente). Acción: Cerrar la llave de paso del gas, ventilar la vivienda y contactar a la empresa de gas, aunque no se perciba olor.

## Categoría CTE · Confort térmico

Preguntas:
- `corrientes_aire`: ¿Corrientes de aire en ventanas o puertas?
- `diferencia_temp`: ¿Diferencias de temperatura entre habitaciones?

Reglas:
- **C01** (Baja, FC 70 %): If corrientes_aire = Sí Then **Sellado deficiente de marcos**. Especialista: Técnico en carpintería / sellado. Acción: Usar burletes temporales en los marcos y evaluar el sellado profesional de ventanas y puertas.
- **C02** (Baja, FC 65 %): If corrientes_aire = No And diferencia_temp = Sí Then **Aislamiento térmico insuficiente**. Especialista: Especialista en aislamiento. Acción: Identificar las zonas con mayor pérdida térmica y considerar mejorar el aislamiento en esos puntos.

## Categoría CAC · Confort acústico

Preguntas:
- `ruido_exterior`: ¿Ruido exterior excesivo?

Reglas:
- **C03** (Baja, FC 65 %): If ruido_exterior = Sí Then **Aislamiento acústico insuficiente**. Especialista: Especialista en acústica. Acción: Evaluar el sellado de ventanas y considerar materiales de aislamiento acústico en la zona más expuesta.
