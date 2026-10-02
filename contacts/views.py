import os
import json
import uuid
import xml.etree.ElementTree as ET
from xml.dom import minidom
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage

from .forms import ContactForm

DATA_DIR = os.path.join(settings.BASE_DIR, "contacts", "data")
os.makedirs(DATA_DIR, exist_ok=True)

ALLOWED_EXT = {".json", ".xml"}
MAX_SIZE = 1 * 1024 * 1024   # 1 МБ

def safe_filename(ext):
    return f"{uuid.uuid4().hex}{ext}"

REQUIRED_FIELDS = {"name", "phone", "email", "category"}


def validate_contacts(data):
    """Проверяет, что data список словарей с нужными полями."""
    if not isinstance(data, list):
        return False, "Корневой элемент должен быть списком контактов"
    for i, item in enumerate(data, 1):
        if not isinstance(item, dict):
            return False, f"Элемент #{i} не является объектом"
        missing = REQUIRED_FIELDS - item.keys()
        if missing:
            return False, f"В контакте #{i} нет полей: {', '.join(missing)}"
        if not all(isinstance(item[k], str) and item[k].strip() for k in REQUIRED_FIELDS):
            return False, f"В контакте #{i} пустые поля"
    return True, ""

def save_json(path, contacts):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(contacts, f, ensure_ascii=False, indent=2)

def save_xml(path, contacts):
    root = ET.Element("contacts")
    for c in contacts:
        node = ET.SubElement(root, "contact")
        for field in ("name", "phone", "email", "category"):
            ET.SubElement(node, field).text = c[field]
    xml_bytes = ET.tostring(root, encoding="utf-8")
    pretty = minidom.parseString(xml_bytes).toprettyxml(indent="  ", encoding="utf-8")
    with open(path, "wb") as f:
        f.write(pretty)

def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def read_xml(path):
    tree = ET.parse(path)
    root = tree.getroot()
    contacts = []
    for node in root.findall("contact"):
        contacts.append({
            "name":     (node.findtext("name") or "").strip(),
            "phone":    (node.findtext("phone") or "").strip(),
            "email":    (node.findtext("email") or "").strip(),
            "category": (node.findtext("category") or "").strip(),
        })
    return contacts

def index(request):
    form = ContactForm()
    if request.method == "POST" and "add_contact" in request.POST:
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.cleaned_data
            fmt = request.POST.get("format", "json")
            ext = ".json" if fmt == "json" else ".xml"
            path = os.path.join(DATA_DIR, safe_filename(ext))

            try:
                if fmt == "json":
                    save_json(path, [contact])
                else:
                    save_xml(path, [contact])
                messages.success(request, f"Контакт сохранён ({fmt.upper()})")
            except Exception as e:
                messages.error(request, f"Ошибка сохранения: {e}")
            return redirect("index")

    if request.method == "POST" and "upload_file" in request.POST:
        uploaded = request.FILES.get("data_file")
        if not uploaded:
            messages.error(request, "Файл не выбран")
        else:
            ext = os.path.splitext(uploaded.name)[1].lower()
            if ext not in ALLOWED_EXT:
                messages.error(request, "Разрешены только .json и .xml")
            elif uploaded.size > MAX_SIZE:
                messages.error(request, "Файл слишком большой (макс. 1 МБ)")
            else:
                filename = safe_filename(ext)
                fs = FileSystemStorage(location=DATA_DIR)
                saved_name = fs.save(filename, uploaded)
                full_path = os.path.join(DATA_DIR, saved_name)

                ok, err = False, ""
                try:
                    if ext == ".json":
                        data = read_json(full_path)
                    else:
                        data = read_xml(full_path)
                    ok, err = validate_contacts(data)
                except Exception as e:
                    ok, err = False, f"Ошибка разбора: {e}"

                if not ok:
                    os.remove(full_path)     
                    messages.error(request, f"Файл невалиден: {err}")
                else:
                    messages.success(request, f"Файл {ext} загружен")

        return redirect("index")

    files_data = []
    try:
        names = sorted(os.listdir(DATA_DIR))
    except FileNotFoundError:
        names = []

    for name in names:
        if name.startswith("."):
            continue
        ext = os.path.splitext(name)[1].lower()
        if ext not in ALLOWED_EXT:
            continue

        path = os.path.join(DATA_DIR, name)
        entry = {"filename": name, "format": ext[1:].upper(), "contacts": [], "error": None}
        try:
            contacts = read_json(path) if ext == ".json" else read_xml(path)
            ok, err = validate_contacts(contacts)
            if ok:
                entry["contacts"] = contacts
            else:
                entry["error"] = err
        except Exception as e:
            entry["error"] = str(e)
        files_data.append(entry)

    return render(request, "contacts/index.html", {
        "form": form,
        "files_data": files_data,
        "has_files": bool(files_data),
    })