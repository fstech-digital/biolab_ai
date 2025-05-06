import asyncio
from extractor import extract_patient_info, detect_lab_type
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python test_extrator_paciente.py <caminho_para_pdf>")
        sys.exit(1)
    file_path = sys.argv[1]

    async def main():
        lab_type = await detect_lab_type(file_path)
        print(f"Tipo de laboratório detectado: {lab_type}")
        info = await extract_patient_info(file_path, lab_type)
        print("Metadados extraídos do paciente:")
        for k, v in info.items():
            print(f"  {k}: {v}")

    asyncio.run(main())
