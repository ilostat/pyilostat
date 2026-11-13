
import ilostat

dataset = "UNE_TUNE_SEX_AGE_NB_A"
note = "R1:2382_T2:85_T3:104"

# Native Python interface
native = ilostat.get_df(
    dataset,
    type="both",
    filters={"note_source": note}
)

# SDMX Python interface
sdmx = ilostat.get_sdmx(
    dataset,
    type="both",
    filters={"NOTE_SOURCE": note}
)

print("\nNative pyilostat:")
print(
    native[["note_source", "note_source.label"]]
    .drop_duplicates()
    .to_string(index=False)
)

print("\nSDMX pyilostat:")
print(
    sdmx[["NOTE_SOURCE", "NOTE_SOURCE_LABEL"]]
    .drop_duplicates()
    .to_string(index=False)
)

expected = set(native["note_source.label"].dropna())
actual = set(sdmx["NOTE_SOURCE_LABEL"].dropna())

assert len(native) > 0, "Native query returned no observations"
assert len(sdmx) > 0, "SDMX query returned no observations"
assert expected == actual, "Combined-note labels differ"

print("\nCombined-note compatibility: PASS")
