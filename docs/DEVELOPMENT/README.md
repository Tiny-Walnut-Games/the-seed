# 🛠️ Development Guidelines

**Coding standards, testing practices, and development workflows.**

---

## 📋 **Development Standards**

### **File Organization**
- **Documentation:** [FILE_ORGANIZATION.md](FILE_ORGANIZATION.md)
- **AI Assistant Guidelines:** [SWEEP_GUIDELINES.md](SWEEP_GUIDELINES.md)

### **Contributing**
- **Guidelines:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **Code Review Process:** Defined in contributing guide

### **Testing**
- **TLDA Tests:** Unity Test Runner
- **Seed Tests:** pytest-based Python tests
- **Bridge Tests:** Integration tests across systems

---

## 🎯 **System Boundaries**

When developing, always respect the three-system architecture:

1. **TLDA (Unity)** - Game engine components
2. **Seed (Python)** - Backend and AI components
3. **Bridges** - Communication between systems

**Never mix responsibilities across boundaries.**

---

## 📚 **Related Documentation**

- **[ARCHITECTURE.md](../ARCHITECTURE.md)** - System architecture overview
- **[TLDA/README.md](../TLDA/README.md)** - Unity development
- **[SEED/README.md](../SEED/README.md)** - Python development

---

**Follow these guidelines to maintain clean, maintainable code for the multiverse project.**
