# Trazabilidad de niebla de guerra y viaje automático

Capacidad 002, rama `spec/jose`. Especificación `c2c5528` y plan/tareas `8524838`.

| Caso | Requisitos | Prueba |
|---|---|---|
| NV-01 | FR-001, FR-002 | [`test_nv01_instante_cero`](../../tests/test_niebla_viaje.py#L137) |
| NV-02 | FR-001, FR-002 | [`test_nv02_visitar_explora_y_avista`](../../tests/test_niebla_viaje.py#L146) |
| NV-03 | FR-003 | [`test_nv03_avistada_y_desconocida_no_revelan`](../../tests/test_niebla_viaje.py#L154) |
| NV-04 | FR-004 | [`test_nv04_y_nv05_recuerdo_de_puertas`](../../tests/test_niebla_viaje.py#L167) |
| NV-05 | FR-004 | [`test_nv04_y_nv05_recuerdo_de_puertas`](../../tests/test_niebla_viaje.py#L167) |
| NV-06 | FR-006 | [`test_nv06_datos_precargados_no_son_conocimiento`](../../tests/test_niebla_viaje.py#L182) |
| NV-07 | FR-008 | [`test_nv07_nv33_rechazo_unico_sin_tiempo`](../../tests/test_niebla_viaje.py#L204) |
| NV-08 | FR-009 | [`test_nv08_menor_costo_frente_a_menos_salas`](../../tests/test_niebla_viaje.py#L213) |
| NV-09 | FR-009 | [`test_nv09_empate_vecina_de_menor_id`](../../tests/test_niebla_viaje.py#L223) |
| NV-10 | FR-004, FR-010 | [`test_nv10_nv11_sin_alternativa_se_detiene_sin_tiempo_extra`](../../tests/test_niebla_viaje.py#L248)<br>[`test_nv10_puerta_recordada_abierta_realmente_cerrada_con_alternativa`](../../tests/test_niebla_viaje.py#L231) |
| NV-11 | FR-010, FR-012 | [`test_nv10_nv11_sin_alternativa_se_detiene_sin_tiempo_extra`](../../tests/test_niebla_viaje.py#L248)<br>[`test_nv11_sin_ruta_al_ordenar`](../../tests/test_niebla_viaje.py#L261) |
| NV-12 | FR-012 | [`test_nv12_enemigos_dormidos_se_activan_y_detienen`](../../tests/test_niebla_viaje.py#L268) |
| NV-13 | FR-012 | [`test_nv13_dano_entre_pasos`](../../tests/test_niebla_viaje.py#L278) |
| NV-14 | FR-011 | [`test_nv14_cada_paso_es_movimiento_ordinario_con_eventos`](../../tests/test_niebla_viaje.py#L287) |
| NV-15 | FR-013 | [`test_nv15_no_abre_puertas_con_llave`](../../tests/test_niebla_viaje.py#L295) |
| NV-16 | FR-014 | [`test_nv16_bitacora_paso_a_paso_y_comentario`](../../tests/test_niebla_viaje.py#L308)<br>[`test_nv16_replay_reproduce_viaje_en_cripta_01`](../../tests/test_niebla_viaje.py#L509) |
| NV-17 | FR-005 | [`test_nv17_nv19_antorcha_explora_vecinas_tras_puertas_cerradas`](../../tests/test_niebla_viaje.py#L375) |
| NV-18 | FR-005 | [`test_nv18_revelar_no_activa_enemigos_ni_trampas`](../../tests/test_niebla_viaje.py#L385) |
| NV-19 | FR-002, FR-005 | [`test_nv17_nv19_antorcha_explora_vecinas_tras_puertas_cerradas`](../../tests/test_niebla_viaje.py#L375) |
| NV-20 | FR-005 | [`test_nv20_sin_antorcha_solo_sala_visitada`](../../tests/test_niebla_viaje.py#L397) |
| NV-21 | FR-007 | [`test_nv21_guardado_previo_a_002_reconstruye_desde_rastro`](../../tests/test_niebla_viaje.py#L430)<br>[`test_nv21_guardar_y_cargar_conserva_conocimiento`](../../tests/test_niebla_viaje.py#L417) |
| NV-22 | FR-007 | [`test_nv22_retroceso_de_entrada_con_antorcha`](../../tests/test_niebla_viaje.py#L438) |
| NV-23 | FR-015 | [`test_nv23_retroceso_durante_viaje_sin_reanudar`](../../tests/test_niebla_viaje.py#L455) |
| NV-24 | FR-007 | [`test_nv24_conocimiento_historico_aislado`](../../tests/test_niebla_viaje.py#L466) |
| NV-25 | FR-018 | [`test_nv25_mapa_solo_conocimiento`](../../tests/test_niebla_viaje.py#L484) |
| NV-26 | FR-012, FR-018 | [`test_nv26_causa_visible`](../../tests/test_niebla_viaje.py#L493) |
| NV-27 | FR-009 | [`test_nv27_avistada_no_es_transito`](../../tests/test_niebla_viaje.py#L316) |
| NV-28 | FR-006 | [`test_nv28_cazador_no_limitado_por_niebla`](../../tests/test_niebla_viaje.py#L193) |
| NV-29 | FR-016, FR-017 | [`test_nv29_bench_caso_requiere_bench`](../../tests/test_bench_niebla_viaje.py#L63)<br>[`test_nv29_contrato_json_desde_main`](../../tests/test_bench_niebla_viaje.py#L23)<br>[`test_nv29_ejecutar_benchmark_sin_archivo`](../../tests/test_bench_niebla_viaje.py#L68)<br>[`test_nv29_preparacion_explora_y_conserva_puertas_cerradas`](../../tests/test_bench_niebla_viaje.py#L11) |
| NV-30 | FR-008 | [`test_nv30_destino_sala_actual`](../../tests/test_niebla_viaje.py#L325) |
| NV-31 | FR-012 | [`test_nv31_enemigos_al_ordenar`](../../tests/test_niebla_viaje.py#L333) |
| NV-32 | FR-012 | [`test_nv32_fin_de_partida_tiene_maxima_prioridad`](../../tests/test_niebla_viaje.py#L356)<br>[`test_nv32_prioridad_de_causas`](../../tests/test_niebla_viaje.py#L345) |
| NV-33 | FR-008 | [`test_nv07_nv33_rechazo_unico_sin_tiempo`](../../tests/test_niebla_viaje.py#L204) |
| NV-34 | FR-004, FR-005, FR-009 | [`test_nv34_antorcha_no_observa_puertas_remotas`](../../tests/test_niebla_viaje.py#L404) |

### Regresión de vistas

- NV-03, NV-25: [salidas en consola](../../tests/test_vista_consola.py#L193).
- NV-03, NV-25: [estado y topología publicados en Pygame](../../tests/vista/test_controlador_pygame.py#L142).
- NV-25: [actualización del minimapa al cambiar el conocimiento](../../tests/vista/test_minimapa_camara.py#L32).
