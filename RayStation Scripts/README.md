# RT-MPH

## RayStation Treatment Planning Automation

A collection of Python-based automation scripts developed to support and streamline treatment planning workflows within **RayStation**.

[![GitHub Stars](https://img.shields.io/github/stars/German-Medical-Institute/RT-MPH?style=for-the-badge\&logo=github)](https://github.com/German-Medical-Institute/RT-MPH/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/German-Medical-Institute/RT-MPH?style=for-the-badge\&logo=github)](https://github.com/German-Medical-Institute/RT-MPH/network/members)
[![GitHub Watchers](https://img.shields.io/github/watchers/German-Medical-Institute/RT-MPH?style=for-the-badge\&logo=github)](https://github.com/German-Medical-Institute/RT-MPH/watchers)
[![License](https://img.shields.io/github/license/German-Medical-Institute/RT-MPH?style=for-the-badge)](https://github.com/German-Medical-Institute/RT-MPH/blob/main/RayStation%20Scripts/LICENSE)
[![Python](https://img.shields.io/badge/Python-Scripting-3776AB?style=for-the-badge\&logo=python\&logoColor=white)](https://www.python.org/)
[![RayStation](https://img.shields.io/badge/RayStation-Scripting-0066CC?style=for-the-badge)](https://www.raysearchlabs.com/)

---

## 📌 Description

**RT-MPH** is a collection of scripting tools intended to assist medical physicists and treatment-planning professionals with repetitive and workflow-specific tasks in RayStation.

The project focuses on improving workflow efficiency, consistency, and reproducibility through automation while maintaining appropriate clinical oversight.

The scripts are written in Python and utilize the RayStation scripting environment and API.

---

## 🎯 Project Objectives

The primary objectives of this project are to:

* Automate repetitive treatment-planning tasks
* Reduce manual data entry and repetitive operations
* Improve workflow consistency
* Support standardized treatment-planning procedures
* Reduce the potential for manual input errors
* Provide reusable tools for treatment-planning workflows
* Maintain version-controlled and documented scripting tools

---

## 📂 Repository Structure

```text
RT-MPH/
│
├── README.md
├── CouchClipping.py
├── CouchClippingPTVs.py
├── SetupBeams.py
├── LICENSE
└── .gitignore
```

---

## 🛠️ Available Scripts

### `CouchClipping.py`

Script designed to assist with couch clipping workflows within RayStation.

**Purpose:**

* Automate couch-related clipping operations
* Reduce repetitive manual workflow steps
* Provide a consistent approach to couch clipping

---

### `CouchClippingPTVs.py`

Script focused on couch clipping workflows involving more than one **Planning Target Volumes (PTVs)**.

**Purpose:**

* Assist with PTV-related couch clipping
* Automate repetitive structure-related operations
* Improve consistency across treatment plans

---

### `SetupBeams.py`

Script providing utilities for treatment beam setup and configuration.

**Purpose:**

* Assist with beam setup
* Automate repetitive beam configuration tasks
* Standardize selected beam parameters

---

## 💻 Requirements

The scripts require an installation of **RayStation** with access to the appropriate scripting functionality.

### Prerequisites

* RayStation
* RayStation scripting enabled
* Python version supported by the installed RayStation release
* Appropriate user permissions

> **Important:** RayStation scripting APIs and supported Python versions may differ between RayStation releases. Compatibility should therefore be verified against the specific RayStation version in use.

---

## 🚀 Usage

1. Clone or download the repository.
2. Navigate to the `RayStation Scripts` directory.
3. Open the required script using the RayStation scripting environment.
4. Review the script and confirm that the intended patient, case, plan, and structures are selected.
5. Execute the script.
6. Review and verify all generated or modified treatment-planning objects before proceeding with clinical use.

Example:

```text
RT-MPH
└── CouchClipping.py
```

---

## ⚠️ Clinical Safety

These scripts are intended to support treatment-planning workflows and **do not replace clinical review or professional judgment**.

Before clinical implementation, scripts should be:

* Tested using appropriate test cases
* Validated against expected results
* Reviewed by qualified personnel
* Verified for compatibility with the local RayStation configuration
* Used in accordance with applicable institutional procedures

All treatment plans and automatically generated or modified objects should undergo the appropriate clinical verification before treatment.

> **The user remains responsible for independently verifying all clinically relevant outputs produced by these scripts.**

---

## 🔬 Development & Validation

Scripts should be tested in a controlled environment before being introduced into routine clinical workflows.

Recommended validation includes:

* Functional testing
* Boundary and error-condition testing
* Verification of generated structures and treatment parameters
* Comparison with manually generated results where appropriate
* Testing across relevant patient geometries
* Compatibility testing across RayStation versions

---

## 📋 Version Control

This project uses Git for source-code version control.

Changes to scripts can therefore be tracked, reviewed, and reverted when necessary.

Repository:

**German Medical Institute — RT-MPH**

---

## 🤝 Contributing

Contributions and suggestions are welcome.

When adding or modifying a script, please provide:

* A clear description of the purpose
* The RayStation version used for development
* Required inputs
* Expected outputs
* Known limitations
* Relevant validation information

Please keep scripts focused, documented, and consistent with the existing project structure.

---

## 📄 License

This project is distributed under the license included in the repository.

See [`RayStation Scripts/LICENSE`](RayStation%20Scripts/LICENSE) for the full license text.

---

## ⭐ Support the Project

If you find this project useful, consider giving the repository a ⭐ on GitHub.

[![Star History Chart](https://api.star-history.com/svg?repos=German-Medical-Institute/RT-MPH\&type=Date)](https://www.star-history.com/#German-Medical-Institute/RT-MPH&Date)

---

## 📈 Project Status

**Status:** Active Development

The repository is intended to evolve as new treatment-planning automation workflows are developed and existing scripts are improved.

---

### Disclaimer

This software is provided for research, development, and workflow-support purposes. It should not be considered a substitute for established clinical procedures, quality assurance processes, or professional medical judgment.
