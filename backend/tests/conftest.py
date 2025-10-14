"""
Pytest Fixtures - Shared Test Fixtures
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """FastAPI TestClient."""
    return TestClient(app)


@pytest.fixture
def sample_fountain_content():
    """Sample Fountain script content."""
    return b"""Title: Test Script
Credit: Written by
Author: Test Author

===

INT. APARTMENT BERLIN - DAY

ANNA (30), a journalist, enters the apartment. She looks stressed.

ANNA
Hello? Anyone here?

She walks through the hallway to the kitchen.

INT. KITCHEN - DAY

PETER (35), her roommate, sits at the table reading a newspaper.

PETER
(without looking up)
Morning.

ANNA
It's three in the afternoon.

PETER
(grins)
For me it's morning.

Anna sits down across from him.

ANNA
We need to talk.

PETER
(puts down newspaper)
That sounds serious.

ANNA
I got the job offer. In Munich.

Peter is silent.

EXT. PARK - DAY

Anna and Peter walk side by side through the park. Autumn leaves fall.

ANNA
Say something.

PETER
What should I say? Congratulations?

ANNA
You could come with me.

PETER
And do what in Munich?

They stop.

ANNA
Make a fresh start. Give us a fresh start.

PETER
(shakes his head)
Berlin is my home.

ANNA
And me? Am I not your home?

Peter doesn't answer. Anna walks on.

INT. APARTMENT BERLIN - NIGHT

Anna packs her suitcases. Peter stands in the doorway.

PETER
You're really leaving.

ANNA
(without looking up)
Tomorrow morning.

PETER
Anna...

She turns to him. Tears in her eyes.

ANNA
I'll wait for you. Three months.

PETER
And then?

ANNA
Then I'll know it's over.

They embrace.

FADE OUT.

THE END
"""


@pytest.fixture
def simple_fountain_content():
    """Simple Fountain script for basic tests."""
    return b"""INT. TEST LOCATION - DAY

Action description here.

CHARACTER
Dialog here.
"""


@pytest.fixture
def multi_scene_fountain():
    """Multi-scene Fountain script."""
    return b"""INT. ROOM A - DAY

First scene.

EXT. ROOM B - NIGHT

Second scene.

INT./EXT. ROOM C - DAWN

Third scene.
"""


@pytest.fixture
def invalid_content():
    """Invalid script content."""
    return b"""This is not a valid screenplay.
Just some random text.
No scene headings at all.
"""
