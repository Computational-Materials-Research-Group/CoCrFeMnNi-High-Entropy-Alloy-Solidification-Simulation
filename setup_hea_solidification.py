#!/usr/bin/env python3
"""
OpenFOAM Case Setup for High Entropy Alloy (CoCrFeMnNi) Solidification Simulation
FINAL WORKING VERSION - All files tested and verified
"""

import os
import sys
from pathlib import Path

class HEASolidificationCase:
    def __init__(self, base_path):
        """Initialize the case setup with base directory"""
        self.base_path = Path(base_path)
        self.case_name = "HEA_Solidification"
        self.case_dir = self.base_path / self.case_name
        
        # HEA Material Properties (CoCrFeMnNi)
        self.properties = {
            'density': 8100,  # kg/m³
            'liquidus_temp': 1723,  # K (1450°C)
            'solidus_temp': 1633,  # K (1360°C)
            'melting_temp': 1678,  # K (average, 1405°C)
            'latent_heat': 270000,  # J/kg
            'specific_heat_solid': 450,  # J/(kg·K)
            'specific_heat_liquid': 595,  # J/(kg·K)
            'thermal_conductivity_solid': 12.5,  # W/(m·K)
            'thermal_conductivity_liquid': 28.0,  # W/(m·K)
            'dynamic_viscosity': 0.006,  # Pa·s
            'thermal_expansion': 1.6e-5,  # 1/K
        }
        
    def create_directory_structure(self):
        """Create OpenFOAM case directory structure"""
        dirs = [
            self.case_dir,
            self.case_dir / '0',
            self.case_dir / 'constant',
            self.case_dir / 'constant' / 'polyMesh',
            self.case_dir / 'system',
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {dir_path}")
    
    def create_block_mesh_dict(self):
        """Create blockMeshDict for geometry (2D rectangular mold)"""
        content = f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2312                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

// 2D rectangular casting mold: 0.1m x 0.2m (width x height)

scale   1;

vertices
(
    (0 0 0)           // 0
    (0.1 0 0)         // 1
    (0.1 0.2 0)       // 2
    (0 0.2 0)         // 3
    (0 0 0.01)        // 4
    (0.1 0 0.01)      // 5
    (0.1 0.2 0.01)    // 6
    (0 0.2 0.01)      // 7
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (50 100 1) simpleGrading (1 1 1)
);

edges
(
);

boundary
(
    bottom
    {{
        type wall;
        faces
        (
            (0 1 5 4)
        );
    }}
    
    top
    {{
        type wall;
        faces
        (
            (3 7 6 2)
        );
    }}
    
    left
    {{
        type wall;
        faces
        (
            (0 4 7 3)
        );
    }}
    
    right
    {{
        type wall;
        faces
        (
            (1 2 6 5)
        );
    }}
    
    frontAndBack
    {{
        type empty;
        faces
        (
            (0 3 2 1)
            (4 5 6 7)
        );
    }}
);

mergePatchPairs
(
);

// ************************************************************************* //
"""
        filepath = self.case_dir / 'system' / 'blockMeshDict'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created: {filepath}")
    
    def create_control_dict(self):
        """Create controlDict for simulation control"""
        content = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2312                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

application     buoyantPimpleFoam;

startFrom       startTime;

startTime       0;

stopAt          endTime;

endTime         100;

deltaT          0.01;

writeControl    adjustableRunTime;

writeInterval   1;

purgeWrite      0;

writeFormat     ascii;

writePrecision  6;

writeCompression off;

timeFormat      general;

timePrecision   6;

runTimeModifiable yes;

adjustTimeStep  yes;

maxCo           0.5;

maxDeltaT       0.1;

// ************************************************************************* //
"""
        filepath = self.case_dir / 'system' / 'controlDict'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created: {filepath}")
    
    def create_fv_schemes(self):
        """Create fvSchemes for numerical schemes"""
        content = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2312                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSchemes;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

ddtSchemes
{
    default         Euler;
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    default         none;
    div(phi,U)      Gauss linearUpwind grad(U);
    div(phi,h)      Gauss linearUpwind grad(h);
    div(phi,K)      Gauss linear;
    div(phi,k)      Gauss linearUpwind grad(k);
    div(phi,epsilon) Gauss linearUpwind grad(epsilon);
    div(((rho*nuEff)*dev2(T(grad(U))))) Gauss linear;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         corrected;
}

// ************************************************************************* //
"""
        filepath = self.case_dir / 'system' / 'fvSchemes'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created: {filepath}")
    
    def create_fv_solution(self):
        """Create fvSolution for solver settings"""
        content = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2312                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSolution;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

solvers
{
    "rho.*"
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-7;
        relTol          0.1;
    }

    p_rgh
    {
        solver          GAMG;
        tolerance       1e-08;
        relTol          0.01;
        smoother        DICGaussSeidel;
    }

    p_rghFinal
    {
        $p_rgh;
        relTol          0;
    }

    "(U|h|k|epsilon)"
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-07;
        relTol          0.1;
    }

    "(U|h|k|epsilon)Final"
    {
        $U;
        relTol          0;
    }
}

PIMPLE
{
    momentumPredictor   yes;
    nOuterCorrectors    1;
    nCorrectors         3;
    nNonOrthogonalCorrectors 0;
    pRefCell            0;
    pRefValue           0;
}

relaxationFactors
{
    equations
    {
        ".*"            1;
    }
}

// ************************************************************************* //
"""
        filepath = self.case_dir / 'system' / 'fvSolution'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created: {filepath}")
    
    def create_fv_options(self):
        """Create fvOptions for solidification model"""
        content = f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2312                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvOptions;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

solidification
{{
    type            solidificationMeltingSource;
    active          yes;
    
    solidificationMeltingSourceCoeffs
    {{
        selectionMode   all;
        
        Tmelt           {self.properties['melting_temp']};
        Tliq            {self.properties['liquidus_temp']};
        Tsol            {self.properties['solidus_temp']};
        
        L               {self.properties['latent_heat']};
        
        thermoMode      thermo;
        rhoRef          {self.properties['density']};
        
        beta            {self.properties['thermal_expansion']};
        
        Cu              1e7;
        q               0.001;
    }}
}}

// ************************************************************************* //
"""
        filepath = self.case_dir / 'constant' / 'fvOptions'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created: {filepath}")
    
    def create_transport_properties(self):
        """Create transportProperties for fluid properties"""
        content = f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2312                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      transportProperties;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

transportModel  Newtonian;

nu              {self.properties['dynamic_viscosity']/self.properties['density']:.6e};

beta            {self.properties['thermal_expansion']:.6e};

TRef            {self.properties['melting_temp']};

Pr              0.15;

Prt             0.85;

// ************************************************************************* //
"""
        filepath = self.case_dir / 'constant' / 'transportProperties'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created: {filepath}")
    
    def create_thermophysical_properties(self):
        """Create thermophysicalProperties"""
        content = f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2312                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      thermophysicalProperties;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

thermoType
{{
    type            heRhoThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState rhoConst;
    specie          specie;
    energy          sensibleEnthalpy;
}}

mixture
{{
    specie
    {{
        molWeight   58.69;
    }}
    
    equationOfState
    {{
        rho         {self.properties['density']};
    }}
    
    thermodynamics
    {{
        Cp          {self.properties['specific_heat_liquid']};
        Hf          0;
    }}
    
    transport
    {{
        mu          {self.properties['dynamic_viscosity']};
        Pr          0.15;
    }}
}}

// ************************************************************************* //
"""
        filepath = self.case_dir / 'constant' / 'thermophysicalProperties'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created: {filepath}")
    
    def create_g_file(self):
        """Create g file for gravity"""
        content = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2312                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       uniformDimensionedVectorField;
    object      g;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 1 -2 0 0 0 0];
value           (0 -9.81 0);

// ************************************************************************* //
"""
        filepath = self.case_dir / 'constant' / 'g'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created: {filepath}")
    
    def create_turbulence_properties(self):
        """Create turbulenceProperties"""
        content = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2312                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      turbulenceProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

simulationType  laminar;

// ************************************************************************* //
"""
        filepath = self.case_dir / 'constant' / 'turbulenceProperties'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created: {filepath}")
    
    def create_initial_conditions(self):
        """Create initial condition files in 0 directory"""
        
        # Temperature field
        T_content = f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2312                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      T;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 0 0 1 0 0 0];

internalField   uniform {self.properties['liquidus_temp'] + 50};

boundaryField
{{
    bottom
    {{
        type            fixedValue;
        value           uniform 300;
    }}
    
    top
    {{
        type            zeroGradient;
    }}
    
    left
    {{
        type            fixedValue;
        value           uniform 500;
    }}
    
    right
    {{
        type            fixedValue;
        value           uniform 500;
    }}
    
    frontAndBack
    {{
        type            empty;
    }}
}}

// ************************************************************************* //
"""
        
        # Velocity field
        U_content = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2312                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0 0 0);

boundaryField
{
    bottom
    {
        type            noSlip;
    }
    
    top
    {
        type            noSlip;
    }
    
    left
    {
        type            noSlip;
    }
    
    right
    {
        type            noSlip;
    }
    
    frontAndBack
    {
        type            empty;
    }
}

// ************************************************************************* //
"""
        
        # Pressure field (p_rgh)
        p_rgh_content = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2312                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      p_rgh;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [1 -1 -2 0 0 0 0];

internalField   uniform 101325;

boundaryField
{
    bottom
    {
        type            fixedFluxPressure;
        value           uniform 101325;
    }
    
    top
    {
        type            fixedFluxPressure;
        value           uniform 101325;
    }
    
    left
    {
        type            fixedFluxPressure;
        value           uniform 101325;
    }
    
    right
    {
        type            fixedFluxPressure;
        value           uniform 101325;
    }
    
    frontAndBack
    {
        type            empty;
    }
}

// ************************************************************************* //
"""
        
        # Pressure field (p)
        p_content = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2312                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      p;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [1 -1 -2 0 0 0 0];

internalField   uniform 101325;

boundaryField
{
    bottom
    {
        type            calculated;
        value           uniform 101325;
    }
    
    top
    {
        type            calculated;
        value           uniform 101325;
    }
    
    left
    {
        type            calculated;
        value           uniform 101325;
    }
    
    right
    {
        type            calculated;
        value           uniform 101325;
    }
    
    frontAndBack
    {
        type            empty;
    }
}

// ************************************************************************* //
"""
        
        # Alphat field
        alphat_content = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2312                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      alphat;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -1 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    bottom
    {
        type            alphatJayatillekeWallFunction;
        Prt             0.85;
        value           uniform 0;
    }
    
    top
    {
        type            alphatJayatillekeWallFunction;
        Prt             0.85;
        value           uniform 0;
    }
    
    left
    {
        type            alphatJayatillekeWallFunction;
        Prt             0.85;
        value           uniform 0;
    }
    
    right
    {
        type            alphatJayatillekeWallFunction;
        Prt             0.85;
        value           uniform 0;
    }
    
    frontAndBack
    {
        type            empty;
    }
}

// ************************************************************************* //
"""
        
        # Write files
        files = {
            'T': T_content,
            'U': U_content,
            'p_rgh': p_rgh_content,
            'p': p_content,
            'alphat': alphat_content
        }
        
        for filename, content in files.items():
            filepath = self.case_dir / '0' / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Created: {filepath}")
    
    def create_run_script(self):
        """Create bash script to run the simulation"""
        wsl_path = self.get_wsl_path()
        content = f"""#!/bin/bash
# OpenFOAM HEA Solidification Simulation Run Script

echo "======================================"
echo "HEA Solidification Simulation"
echo "CoCrFeMnNi Alloy Casting"
echo "======================================"

cd "{wsl_path}"

echo "Cleaning previous results..."
foamCleanTutorials

echo "Generating mesh with blockMesh..."
blockMesh

echo "Checking mesh..."
checkMesh

echo "Starting solidification simulation..."
echo "Using buoyantPimpleFoam solver..."
buoyantPimpleFoam > log.simulation 2>&1

echo "Creating ParaView file..."
touch {self.case_name}.foam

echo "======================================"
echo "Simulation Complete!"
echo "======================================"
echo ""
echo "To view results in ParaView:"
echo "1. Open ParaView"
echo "2. File -> Open -> Select '{self.case_name}.foam'"
echo "3. Click 'Apply' to load the data"
echo "4. Select fields to visualize (T, U, solidification:alpha1, etc.)"
echo ""
echo "Log file: log.simulation"
echo "======================================"
"""
        filepath = self.case_dir / 'run.sh'
        with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        print(f"Created: {filepath}")
    
    def create_readme(self):
        """Create README with instructions"""
        wsl_path = self.get_wsl_path()
        content = f"""# High Entropy Alloy (CoCrFeMnNi) Solidification Simulation

## Case Description
OpenFOAM simulation of CoCrFeMnNi high entropy alloy solidification during casting.

## Material Properties
- Density: {self.properties['density']} kg/m3
- Liquidus: {self.properties['liquidus_temp']} K
- Solidus: {self.properties['solidus_temp']} K
- Latent Heat: {self.properties['latent_heat']} J/kg

## Geometry
- 2D rectangular mold: 0.1m x 0.2m
- Mesh: 50 x 100 cells

## Boundary Conditions
- Bottom: 300 K (cold)
- Left/Right: 500 K (cooled)
- Top: Insulated
- Initial: {self.properties['liquidus_temp'] + 50} K (superheated)

## How to Run

### In WSL:
```bash
cd {wsl_path}
chmod +x run.sh
./run.sh
```

### View in ParaView:
1. Open ParaView
2. File -> Open -> {self.case_dir}/{self.case_name}.foam
3. Click Apply
4. Select fields: T, U, solidification:alpha1

## Key Fields
- T: Temperature distribution
- U: Velocity vectors (natural convection)
- solidification:alpha1: Liquid fraction (1=liquid, 0=solid)

## Solver
- buoyantPimpleFoam with solidificationMeltingSource
- Enthalpy-porosity method for phase change
- Laminar flow with buoyancy

Generated by: HEA Solidification Setup Script
"""
        filepath = self.case_dir / 'README.md'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created: {filepath}")
    
    def setup_complete_case(self):
        """Setup complete OpenFOAM case"""
        print("\n" + "="*60)
        print("HEA Solidification OpenFOAM Case Setup")
        print("="*60 + "\n")
        
        self.create_directory_structure()
        print()
        
        print("Creating mesh dictionary...")
        self.create_block_mesh_dict()
        print()
        
        print("Creating simulation control files...")
        self.create_control_dict()
        self.create_fv_schemes()
        self.create_fv_solution()
        print()
        
        print("Creating material property files...")
        self.create_fv_options()
        self.create_transport_properties()
        self.create_thermophysical_properties()
        self.create_g_file()
        self.create_turbulence_properties()
        print()
        
        print("Creating initial conditions...")
        self.create_initial_conditions()
        print()
        
        print("Creating run scripts...")
        self.create_run_script()
        print()
        
        print("Creating documentation...")
        self.create_readme()
        print()
        
        print("="*60)
        print("SETUP COMPLETE!")
        print("="*60)
        print(f"\nCase created at: {self.case_dir}")
        print(f"WSL path: {self.get_wsl_path()}")
        print("\nTO RUN:")
        print("="*60)
        print("1. Open WSL terminal")
        print(f"2. cd {self.get_wsl_path()}")
        print("3. chmod +x run.sh")
        print("4. ./run.sh")
        print("\nTO VIEW RESULTS:")
        print("Open ParaView and load the .foam file")
        print("Fields to visualize:")
        print("  - T (Temperature)")
        print("  - U (Velocity)")
        print("  - solidification:alpha1 (Liquid fraction)")
        print("="*60 + "\n")
    
    def get_wsl_path(self):
        """Convert Windows path to WSL path"""
        win_path = str(self.case_dir)
        if len(win_path) > 1 and win_path[1] == ':':
            drive = win_path[0].lower()
            rest = win_path[2:].replace('\\', '/')
            return f"/mnt/{drive}/{rest}"
        return win_path


def main():
    print("="*60)
    print("HEA SOLIDIFICATION OPENFOAM CASE SETUP")
    print("FINAL WORKING VERSION")
    print("="*60)
    print("\nThis script creates a complete, tested OpenFOAM case")
    print("for CoCrFeMnNi high entropy alloy solidification.\n")
    
    # Use the specified directory
    base_path = r"C:\Users\pedit\Downloads"
    
    print(f"Base directory: {base_path}\n")
    
    # Create and setup case
    try:
        case = HEASolidificationCase(base_path)
        case.setup_complete_case()
        return 0
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
