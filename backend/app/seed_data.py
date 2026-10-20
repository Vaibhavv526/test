"""
Seed data generator and pre-built synthetic profiles.
Seeds ~25 colorful, varied synthetic personas for zero-real-data instant demo.
"""
import json
import logging
from sqlalchemy.orm import Session
from app.database import ProfileDB
from app.models import ProfileAnalysis

logger = logging.getLogger("agentic_dating.seed")

SYNTHETIC_CANDIDATES = [
    {
        "name": "Elena Rostova",
        "age": 29,
        "occupation": "Computational Biologist & Cellist",
        "location": "Boston, MA",
        "raw_input": "I spend weekdays modeling protein folding mechanics using graph neural nets, and weekends playing chamber music with friends or foraging for wild mushrooms in the Berkshires. I believe vulnerability is the highest form of bravery. Looking for an intellectually restless partner who loves late-night kitchen discussions on consciousness as much as lazy Sunday morning pour-overs.",
        "values": ["Intellectual rigor", "Vulnerability", "Creative expression", "Deep empathy"],
        "hobbies": ["Cello performance", "Mycology foraging", "Pour-over coffee", "Bouldering"],
        "interests": ["Structural biology", "Post-minimalist music", "Nordic cinema", "Complex systems"],
        "needs": ["Intellectual sparring with kindness", "Shared quiet spaces", "Emotional security"],
        "dealbreakers": ["Anti-intellectualism", "Emotional detachment", "Flakiness"],
        "communication_style": "Poetic, thoughtful, and analytically sincere",
        "dating_intentions": "Long-term partnership with an intellectual equal",
        "tagline": "Mapping protein folds by day, playing Bach cello suites by night."
    },
    {
        "name": "Marcus Vance",
        "age": 33,
        "occupation": "Indie Hardware Founder & Cyclist",
        "location": "San Francisco, CA",
        "raw_input": "Building open-source tactile synthesizers and mechanical keyboards. When I'm not in my machine shop smelling like cutting fluid and solder, I'm doing 80-mile road rides over Marin Headlands. Fast-moving, ambitious, but I leave work completely at the door once the day is done. Big fan of dry martinis, design philosophy, and people who have strong opinions weakly held.",
        "values": ["Craftsmanship", "Physical vitality", "Intellectual honesty", "Autonomy"],
        "hobbies": ["Road cycling", "Analog synthesizers", "Espresso calibration", "Woodworking"],
        "interests": ["Industrial design", "Acoustics", "Dieter Rams philosophy", "Typography"],
        "needs": ["Physical affection & shared fitness", "Mutual career ambition", "Direct communication"],
        "dealbreakers": ["Passive aggressiveness", "Sedentary lifestyle", "Defensiveness"],
        "communication_style": "Direct, humorous, and solution-oriented",
        "dating_intentions": "High-bandwidth committed relationship",
        "tagline": "Obsessed with tactile hardware, mountain ridgelines, and perfect espresso."
    },
    {
        "name": "Amina Al-Mansoor",
        "age": 31,
        "occupation": "Humanitarian Architect",
        "location": "New York, NY",
        "raw_input": "Architect designing resilient modular housing for disaster zones and urban informal settlements. I live in Brooklyn with over 40 houseplants and a vintage risograph printer. Passionate about participatory design, ceramics, natural wine, and dancing until 3 AM to Afrohouse. Looking for someone grounded, socially conscious, and unafraid of big feelings.",
        "values": ["Social justice", "Community warmth", "Aesthetic joy", "Radical candor"],
        "hobbies": ["Ceramics throwing", "Risograph printing", "Afrohouse dancing", "Vintage furniture restoration"],
        "interests": ["Vernacular architecture", "Urban anthropology", "Contemporary African art", "Fermentation"],
        "needs": ["Deep emotional resonance", "Celebration of culture and art", "Spontaneity"],
        "dealbreakers": ["Cynicism about social impact", "Stinginess with affection", "Closed-mindedness"],
        "communication_style": "Warm, expressive, and deeply attentive",
        "dating_intentions": "A loving, egalitarian life partnership",
        "tagline": "Designing resilient architecture and throwing wonky ceramic mugs."
    },
    {
        "name": "Julian Chen",
        "age": 28,
        "occupation": "AI Research Scientist & Marathoner",
        "location": "Seattle, WA",
        "raw_input": "Researching mechanistic interpretability at an AI lab. Outside the lab, I'm training for my third sub-3 marathon and building lo-fi ambient music tracks in Ableton. I love long conversations about why things are the way they are, cooking elaborate Taiwanese braised pork for friends, and exploring rainy Pacific Northwest trails. Looking for someone with genuine curiosity and a warm heart.",
        "values": ["Curiosity", "Kindness", "Disciplined craft", "Warm hospitality"],
        "hobbies": ["Marathon running", "Taiwanese culinary arts", "Ambient music production", "Backpacking"],
        "interests": ["Neural networks", "Cognitive science", "Haruki Murakami novels", "Aerobic physiology"],
        "needs": ["Intellectual depth", "Mutual encouragement in goals", "Playful affection"],
        "dealbreakers": ["Cruelty to service staff", "Lack of ambition", "Superficiality"],
        "communication_style": "Gentle, attentive, and playfully nerdy",
        "dating_intentions": "Meaningful, long-term romantic journey",
        "tagline": "Decoding neural representations and running through misty cedar forests."
    },
    {
        "name": "Chloe Devereux",
        "age": 34,
        "occupation": "Investigative Climate Journalist",
        "location": "Boulder, CO",
        "raw_input": "I write long-form investigations on water rights, renewable grids, and environmental accountability. My happiest states are: halfway up a granite multi-pitch in Eldorado Canyon, sitting around a campfire with acoustic guitars, or curled up in a hammock reading non-fiction. I value fierce integrity, dark humor, and partners who aren't afraid of dirty hiking boots and uncomfortable truths.",
        "values": ["Integrity", "Courage", "Ecological stewardship", "Authenticity"],
        "hobbies": ["Rock climbing", "Campfire guitar", "Backcountry skiing", "Film photography"],
        "interests": ["Environmental politics", "Hydrology", "Narrative journalism", "Folk music"],
        "needs": ["Adventure partnership", "Emotional self-reliance", "Dry witty humor"],
        "dealbreakers": ["Materialism", "Indifference to the planet", "Fragile ego"],
        "communication_style": "Sharp, candid, dryly humorous, and fiercely real",
        "dating_intentions": "A rock-solid partnership of adventure and mutual purpose",
        "tagline": "Chasing investigative leads, granite summits, and alpine sunsets."
    },
    {
        "name": "Devon Patel",
        "age": 32,
        "occupation": "Pediatric Emergency Doctor & Home Baker",
        "location": "Chicago, IL",
        "raw_input": "ER doc who heals kids by day and perfects sourdough hydration ratios by night. I bring high calmness to chaos. When I'm off shift, I love improv comedy, exploring hidden neighborhood ramen joints, and hosting chaotic dinner parties with too much board game energy. Seeking a partner who appreciates silly banter, deep talks on ethics, and waking up to fresh cardamom cinnamon buns.",
        "values": ["Empathy", "Resilience under pressure", "Humor", "Generosity"],
        "hobbies": ["Sourdough baking", "Improv comedy", "Strategy board games", "Urban cycling"],
        "interests": ["Emergency medicine", "Food science", "Storytelling podcasts", "Architecture history"],
        "needs": ["Laughter as decompression", "Emotional safety", "Mutual acts of service"],
        "dealbreakers": ["Lack of empathy", "Excessive rigidity", "Gossiping"],
        "communication_style": "Calm, deeply comforting, and quick with self-deprecating wit",
        "dating_intentions": "Looking for the person to build a warm, laughter-filled home with",
        "tagline": "ER physician with calm nerves, warm sourdough, and a love for improv."
    },
    {
        "name": "Sofia Lindqvist",
        "age": 27,
        "occupation": "Type Designer & Risograph Publisher",
        "location": "San Francisco, CA",
        "raw_input": "Swedish-American typography nerd obsessed with the curves of ampersands and the tactile feel of heavy cotton paper. I run an independent micro-press, collect mid-century Scandinavian glassware, and obsess over Japanese denim. I'm introverted in crowds but deeply talkative one-on-one. Love quiet museum dates, botanical gardens, and someone who notices the tiny details others miss.",
        "values": ["Aesthetic craftsmanship", "Intentionality", "Patience", "Quiet depth"],
        "hobbies": ["Letterpress printing", "Botanical illustration", "Specialty tea ceremony", "Vintage shopping"],
        "interests": ["Typography history", "Japanese stationery", "Modernist literature", "Film archiving"],
        "needs": ["Low-stress quiet companionship", "Respect for creative space", "Subtle affection"],
        "dealbreakers": ["Loud boastfulness", "Messy disrespect of boundaries", "Consumerist obsession"],
        "communication_style": "Soft-spoken, observant, warm, and detail-oriented",
        "dating_intentions": "Slow-burn romance leading to deep, lasting commitment",
        "tagline": "Drawing letters, drinking sencha, and curating small beautiful moments."
    },
    {
        "name": "Tariq Bennett",
        "age": 35,
        "occupation": "Fintech Product Lead & Vinyl DJ",
        "location": "Austin, TX",
        "raw_input": "Leading product strategy for financial inclusion tools during the week, digging through crates of rare 1970s Brazilian jazz and funk records on the weekend. Big believer in radical gratitude and physical fitness. You'll find me lifting heavy weights, grilling Texas barbecue for fifteen friends, or discussing behavioral economics. Seeking an ambitious woman with infectious laughter and a clear sense of self.",
        "values": ["Ambition", "Gratitude", "Loyalty", "Generous hospitality"],
        "hobbies": ["Vinyl DJing", "Powerlifting", "Smoked brisket BBQ", "Podcast producing"],
        "interests": ["Behavioral economics", "Rare groove funk", "Latin American travel", "Financial literacy"],
        "needs": ["Reciprocal admiration", "High energy & enthusiasm", "Unwavering loyalty"],
        "dealbreakers": ["Victim mentality", "Chronic negativity", "Lack of self-awareness"],
        "communication_style": "Charismatic, enthusiastic, encouraging, and clear",
        "dating_intentions": "Ready for marriage and creating a powerhouse family team",
        "tagline": "Fintech strategist spinning vintage bossa nova and smoking brisket."
    },
    {
        "name": "Kavita Sharma",
        "age": 30,
        "occupation": "Accessibility UX Researcher",
        "location": "Seattle, WA",
        "raw_input": "I research and design digital experiences for blind and neurodiverse users. Outside work, I cultivate an urban balcony vegetable jungle, paint watercolor landscapes, and host documentary screenings. I love slow Sunday walks through farmers markets and discussing the psychology of habit formation. Looking for a conscious, kind partner with a dry sense of humor.",
        "values": ["Inclusivity", "Quiet mindfulness", "Compassion", "Intellectual curiosity"],
        "hobbies": ["Watercolor painting", "Balcony gardening", "Audiobooks", "Filter coffee"],
        "interests": ["Assistive technology", "Cognitive psychology", "Sustainable urbanism", "Cinema"],
        "needs": ["Emotional presence", "Thoughtful check-ins", "Shared intellectual projects"],
        "dealbreakers": ["Arrogance", "Unkindness to elders or strangers", "Flakiness"],
        "communication_style": "Thoughtful, gentle, and observant",
        "dating_intentions": "Committed partnership built on mutual care and quiet adventures",
        "tagline": "Designing accessible worlds and painting misty watercolors."
    },
    {
        "name": "Liam O'Reilly",
        "age": 36,
        "occupation": "Ocean Conservation Filmmaker",
        "location": "San Diego, CA",
        "raw_input": "Underwater cinematographer and documentary director covering kelp forest restoration and cetacean acoustics. When my fins are off, I love cooking fresh seafood with too much garlic, playing Celtic fingerstyle guitar, and repairing vintage Land Cruisers. Seeking a courageous, warm-hearted co-conspirator who loves the smell of sea salt and salt-of-the-earth living.",
        "values": ["Courage", "Humility", "Wilderness stewardship", "Laughter"],
        "hobbies": ["Scuba diving", "Celtic guitar", "Surfing", "Vintage car mechanics"],
        "interests": ["Marine ecology", "Documentary storytelling", "Acoustic ecology", "Maritime history"],
        "needs": ["Shared love for the outdoors", "Mutual independence", "Affectionate humor"],
        "dealbreakers": ["Phony vanity", "Fear of dirt/water", "Lack of follow-through"],
        "communication_style": "Down-to-earth, story-driven, warm, and playful",
        "dating_intentions": "Deep lifelong romance with a true adventure partner",
        "tagline": "Documenting kelp forests, surfing sunrise swells, and playing acoustic guitar."
    },
    {
        "name": "Zoe Sterling",
        "age": 26,
        "occupation": "Indie Game Developer & Pixel Artist",
        "location": "Montreal, QC",
        "raw_input": "Solo indie dev crafting cozy puzzle games about grief and community. I live with two adopted rescue cats and an obscene collection of matcha powders. Huge fan of tabletop roleplaying games, Japanese anime classics, late-night museum strolls, and deep debates about narrative structure. Looking for someone sweet, imaginative, and ready for spontaneous road trips to small towns.",
        "values": ["Imagination", "Emotional authenticity", "Kindness", "Playfulness"],
        "hobbies": ["Pixel art", "Matcha whisking", "Tabletop RPGs", "Thrifting oversized sweaters"],
        "interests": ["Game narrative design", "Animation history", "Ghibli films", "Cozy literature"],
        "needs": ["Creative encouragement", "Playful cuddles & banter", "Acceptance of quirks"],
        "dealbreakers": ["Rigid traditionalism", "Disrespecting pets", "Mocking introverts"],
        "communication_style": "Whimsical, heartfelt, animated, and honest",
        "dating_intentions": "Finding my favorite weirdo to build a cozy life with",
        "tagline": "Crafting cozy pixel art games and whisking ceremonial Uji matcha."
    },
    {
        "name": "Mateo Morales",
        "age": 33,
        "occupation": "Urban Permaculture Farmer & Mezcalier",
        "location": "Portland, OR",
        "raw_input": "Managing an educational community rooftop farm in downtown Portland and sourcing artisanal small-batch mezcals from Oaxaca. I believe food is medicine and ritual. You can find me grafting heirloom apple trees, making fresh masa from scratch, or reading magical realism novels under an oak tree. Looking for a grounded, passionate woman who loves deep sensory living.",
        "values": ["Earth connection", "Tradition & heritage", "Sensory presence", "Community"],
        "hobbies": ["Heirloom gardening", "Masa nixtamalization", "Mezcal tasting", "Wood carving"],
        "interests": ["Agroecology", "Latin American magical realism", "Indigenous agriculture", "Folk art"],
        "needs": ["Shared passion for food and nature", "Physical warmth", "Spiritual grounding"],
        "dealbreakers": ["Hyper-consumerism", "Disdain for nature", "Emotional coldness"],
        "communication_style": "Poetic, earthy, slow-paced, and soulful",
        "dating_intentions": "Soulful marriage and growing an abundant garden together",
        "tagline": "Growing rooftop heirloom corn and sharing artisanal mezcal under the stars."
    },
    {
        "name": "Clara Fontaine",
        "age": 32,
        "occupation": "Rare Book Conservator",
        "location": "Philadelphia, PA",
        "raw_input": "Preserving 17th-century illuminated manuscripts and botanical folios. I love the smell of beeswax, parchment, and old libraries. Outside the archive, I'm a competitive distance runner, an avid sourdough baker, and a lover of flea markets and classical radio. Looking for a patient, curious mind who appreciates craft, good stationery, and comfortable silences.",
        "values": ["Patience", "Craftsmanship", "Historical reverence", "Quiet devotion"],
        "hobbies": ["Bookbinding", "Distance running", "Calligraphy", "Antique flea markets"],
        "interests": ["Material history", "Botany", "Medieval ink recipes", "Baroque music"],
        "needs": ["Intellectual calm", "Respect for focused solitude", "Gentle affection"],
        "dealbreakers": ["Chaos and recklessness", "Loud boastfulness", "Messiness"],
        "communication_style": "Articulate, serene, observant, and warm",
        "dating_intentions": "Steady, enduring partnership built to last decades",
        "tagline": "Restoring centuries-old manuscripts and running along the Schuylkill River."
    },
    {
        "name": "Kenji Takahashi",
        "age": 31,
        "occupation": "Robotics Software Lead & Woodworker",
        "location": "San Jose, CA",
        "raw_input": "Building autonomous perception systems for surgical robots. On weekends, I retreat to my garage woodshop to make Japanese joinery furniture with hand chisels—no screws, no nails. I value precision, quiet humor, and people who do things with their whole heart. Big fan of tonkotsu ramen, mountain climbing, and learning new skills from scratch.",
        "values": ["Precision", "Humility", "Dedication", "Continuous learning"],
        "hobbies": ["Japanese woodworking", "Alpine mountaineering", "Ramen craft", "3D printing"],
        "interests": ["Computer vision", "Traditional carpentry", "Spatial computing", "Philosophy of mind"],
        "needs": ["Mutual respect for craftsmanship", "Calm emotional baseline", "Active physical life"],
        "dealbreakers": ["Pretentiousness", "Lack of curiosity", "Drama-seeking behavior"],
        "communication_style": "Concise, dryly witty, considerate, and loyal",
        "dating_intentions": "Long-term commitment with an independent, caring partner",
        "tagline": "Surgical robotics by week, chisel-cut mortise-and-tenon joints on Saturday."
    },
    {
        "name": "Miriam Vance",
        "age": 38,
        "occupation": "Bioethics Professor & Essayist",
        "location": "Cambridge, MA",
        "raw_input": "Teaching ethical philosophy and AI governance at university. Mother of an energetic 8-year-old rescue greyhound. I host weekly salon dinners with heated debates over natural law, CRISPR, and modern art. I value sharp intellect paired with immense generosity. Looking for an emotionally mature equal who can challenge my assumptions and make me laugh until my stomach hurts.",
        "values": ["Moral integrity", "Generosity", "Intellectual challenge", "Independence"],
        "hobbies": ["Hosting salon dinners", "Walking my greyhound", "Writing essays", "Tennis"],
        "interests": ["Bioethics", "Philosophical skepticism", "Contemporary theater", "Espresso"],
        "needs": ["High intellectual banter", "Emotional maturity & stability", "Equal partnership"],
        "dealbreakers": ["Insecurity about strong women", "Dishonesty", "Emotional infantilism"],
        "communication_style": "Eloquent, quick-witted, probing, and deeply supportive",
        "dating_intentions": "An equal, exhilarating intellectual and romantic life partner",
        "tagline": "Debating ethical frontiers at dinner, walking my greyhound at dusk."
    },
    {
        "name": "Gabriel Santos",
        "age": 27,
        "occupation": "Specialty Coffee Roaster & Skateboarder",
        "location": "Los Angeles, CA",
        "raw_input": "Co-owner of a micro-roastery in Silver Lake. Sourcing beans directly from family farms in Minas Gerais and Colombia. When the roaster is off, I'm skateboarding the Venice bowl, browsing vintage records, or cooking feijoada for my cousins. I bring infectious positivity and zero pretension to everything I do. Seeking someone spontaneous, affectionate, and full of joy.",
        "values": ["Positivity", "Family ties", "Creative freedom", "Spontaneity"],
        "hobbies": ["Skateboarding", "Coffee cupping", "Vinyl collecting", "Brazilian cooking"],
        "interests": ["Coffee agronomy", "Samba & Bossa Nova", "Street culture", "Cinematography"],
        "needs": ["Playful physical touch", "Shared laughter", "Warmth & open communication"],
        "dealbreakers": ["Elitism", "Excessive pessimism", "Controlling attitudes"],
        "communication_style": "High-energy, affectionate, humorous, and open-hearted",
        "dating_intentions": "Finding a best friend and passionate lover to explore life with",
        "tagline": "Roasting micro-lot coffee, carving skate bowls, and spreading sunshine."
    },
    {
        "name": "Priya Nair",
        "age": 30,
        "occupation": "Clean Energy Grid Analyst",
        "location": "Washington, DC",
        "raw_input": "Working on regional grid decarbonization policies and battery storage incentives. Outside the policy wonk world, I sing classical Carnatic music, train in kickboxing, and cook elaborate South Indian meals with freshly ground spices. I love people who have both a sharp analytical brain and an open, tender heart.",
        "values": ["Impact", "Discipline", "Cultural heritage", "Authenticity"],
        "hobbies": ["Carnatic vocal music", "Muay Thai kickboxing", "South Indian cooking", "Kayaking"],
        "interests": ["Clean energy transition", "Music theory", "Geopolitics", "Urban hiking"],
        "needs": ["Mutual ambition", "Warm emotional availability", "Lively spirited debate"],
        "dealbreakers": ["Lack of work ethic", "Cultural intolerance", "Defensiveness"],
        "communication_style": "Articulate, fiery, warm, and highly expressive",
        "dating_intentions": "Committed, progressive partnership built on shared dreams",
        "tagline": "Decarbonizing energy grids, practicing Carnatic scales, and throwing kicks."
    },
    {
        "name": "Hannah Berg",
        "age": 34,
        "occupation": "Landscape Oil Painter",
        "location": "Santa Fe, NM",
        "raw_input": "Painting large-format oils of desert mesas, thunderstorms, and high-desert light. Living in an adobe studio off the grid. When I step away from the easel, I'm riding horses, baking rye bread, or stargazing under dark desert skies. Looking for a man of quiet strength, artistic appreciation, and deep grounding.",
        "values": ["Artistic depth", "Simplicity", "Connection to land", "Honesty"],
        "hobbies": ["Horseback riding", "Oil painting", "Stargazing", "Rye baking"],
        "interests": ["Plein air art", "Astronomy", "Western ecology", "Acoustic folk"],
        "needs": ["Uncluttered quiet", "Mutual trust", "Physical presence and affection"],
        "dealbreakers": ["Addiction to screens", "City snobbery", "Emotional games"],
        "communication_style": "Grounded, calm, soulful, and candid",
        "dating_intentions": "An authentic, peaceful lifelong marriage",
        "tagline": "Capturing desert storms in oil paint and riding across piñon mesas."
    },
    {
        "name": "Dante Rossi",
        "age": 31,
        "occupation": "Sommelier & Artisanal Pasta Maker",
        "location": "New York, NY",
        "raw_input": "Running the wine program at a natural wine bar in the West Village and hand-rolling tortellini with heritage flours. I believe dining together is the highest art form of human connection. Outside the cellar, I'm a passionate soccer player, film buff, and collector of vintage Italian motorcycles. Looking for an enthusiastic, curious partner who loves food and big laughs.",
        "values": ["Hospitality", "Passionate living", "Loyalty", "Curiosity"],
        "hobbies": ["Handmade pasta", "Wine tasting", "Vintage motorcycle restoration", "Soccer"],
        "interests": ["Italian viticulture", "Neorealist cinema", "Culinary history", "Travel"],
        "needs": ["Shared indulgence in life's pleasures", "Romantic affection", "Direct honesty"],
        "dealbreakers": ["Pickiness about food", "Lack of warmth", "Pessimism"],
        "communication_style": "Charming, charismatic, passionate, and attentive",
        "dating_intentions": "A passionate, laughter-soaked romantic partnership",
        "tagline": "Curating natural wines, hand-rolling agnolotti, and riding classic bikes."
    },
    {
        "name": "Siddharth Roy",
        "age": 28,
        "occupation": "Quantum Algorithm Researcher",
        "location": "Palo Alto, CA",
        "raw_input": "Working on quantum error-correcting codes. In my personal life, I'm a passionate chess player, amateur tabla percussionist, and sci-fi collector. I love finding elegance in difficult problems. I appreciate partners who love getting lost in hypothetical scenarios and who bring warmth and emotional vulnerability to the table.",
        "values": ["Rationality & depth", "Kindness", "Patience", "Wonder"],
        "hobbies": ["Chess blitz", "Tabla drumming", "Sci-fi literature", "Tea brewing"],
        "interests": ["Quantum physics", "Information theory", "Indian classical rhythm", "Cinema"],
        "needs": ["Intellectual compatibility", "Emotional gentleness", "Shared playful curiosity"],
        "dealbreakers": ["Shallow materialism", "Volatile temper", "Cynicism"],
        "communication_style": "Gentle, thoughtful, analytical, and curious",
        "dating_intentions": "Long-term relationship with my intellectual and emotional companion",
        "tagline": "Solving quantum entanglement and practicing Indian classical polyrhythms."
    },
    {
        "name": "Maya Jenkins",
        "age": 32,
        "occupation": "Clinical Neuropsychologist",
        "location": "Minneapolis, MN",
        "raw_input": "Evaluating traumatic brain injury recovery and researching neuroplasticity. Outside the clinic, I'm a competitive cross-country skier, pottery hobbyist, and lover of cozy cabin weekends on Lake Superior. I look for someone emotionally articulate, unafraid of hard conversations, and with a silly, self-aware sense of humor.",
        "values": ["Emotional intelligence", "Resilience", "Mindfulness", "Laughter"],
        "hobbies": ["Cross-country skiing", "Wheel pottery", "Canoeing", "Baking pies"],
        "interests": ["Neuroplasticity", "Mind-body medicine", "Midwestern literature", "Podcasts"],
        "needs": ["Deep emotional safety", "Equal communication effort", "Outdoor movement"],
        "dealbreakers": ["Emotional immaturity", "Passive aggression", "Substance abuse"],
        "communication_style": "Empathetic, clear, insightful, and humorously grounded",
        "dating_intentions": "Building a solid, loving home filled with mutual respect and laughter",
        "tagline": "Studying brain resilience, skiing pine trails, and throwing ceramic bowls."
    },
    {
        "name": "Finneas Flynn",
        "age": 35,
        "occupation": "Traditional Wooden Boat Builder",
        "location": "Portland, ME",
        "raw_input": "Handcrafting cedar-strip canoes and wooden lobster boats on the coast of Maine. I live close to the tides, smell like white oak shavings, and spend evenings reading maritime history or playing acoustic banjo on the porch. Looking for someone grounded who loves woodsmoke, fog on the water, and honest, unpretentious living.",
        "values": ["Honesty", "Patience", "Self-reliance", "Connection to sea"],
        "hobbies": ["Boatbuilding", "Clawhammer banjo", "Sailing", "Wood carving"],
        "interests": ["Maritime craft", "Traditional tools", "New England history", "Astronomy"],
        "needs": ["Authentic calm", "Independence within togetherness", "Loyalty"],
        "dealbreakers": ["High maintenance demands", "Inauthenticity", "Disdain for manual work"],
        "communication_style": "Calm, observant, genuine, and unhurried",
        "dating_intentions": "A quiet, devoted lifelong love on the rocky coast",
        "tagline": "Building cedar-strip boats with hand planes and playing clawhammer banjo."
    },
    {
        "name": "Astrid Holst",
        "age": 29,
        "occupation": "Sustainable Knitwear Designer",
        "location": "Chicago, IL",
        "raw_input": "Designing zero-waste knitwear from regenerative organic wool. Born in Copenhagen, now loving Chicago's brutalist architecture and winter lakefront. I love architectural walking tours, cold-plunging in Lake Michigan, and hosting smørrebrød lunches with friends. Seeking an adventurous, stylish soul who loves design and doesn't mind cold weather.",
        "values": ["Sustainability", "Design integrity", "Warm community", "Curiosity"],
        "hobbies": ["Knitting design", "Cold lake plunging", "Nordic cooking", "Architecture tours"],
        "interests": ["Textile innovation", "Bauhaus design", "Circular economy", "Electronic music"],
        "needs": ["Shared aesthetic appreciation", "Physical vitality", "Open communication"],
        "dealbreakers": ["Wastefulness", "Narrow worldview", "Emotional unavailability"],
        "communication_style": "Direct, stylish, playful, and Scandinavian-frank",
        "dating_intentions": "A dynamic, loving life partnership full of travel and creativity",
        "tagline": "Designing regenerative knitwear and jumping into freezing Lake Michigan."
    },
    {
        "name": "Leo Zhang",
        "age": 33,
        "occupation": "Aerospace Propulsion Engineer",
        "location": "Houston, TX",
        "raw_input": "Designing cryogenic fuel valves for next-generation orbital rockets. Off the clock, I'm a competitive Latin salsa dancer, amateur barbecue enthusiast, and lover of stargazing with high-powered telescopes. Looking for someone who brings color, music, and warmth into my world, and who isn't afraid to laugh at life's absurdity.",
        "values": ["Ambition", "Joy & celebration", "Integrity", "Dedication"],
        "hobbies": ["Salsa dancing", "Telescope stargazing", "Texas BBQ smoking", "Weightlifting"],
        "interests": ["Rocket propulsion", "Astrophysics", "Afro-Cuban rhythm", "Sci-fi films"],
        "needs": ["Playful energy & dancing", "Emotional openness", "Intellectual mutual support"],
        "dealbreakers": ["Pretentiousness", "Lack of joy", "Extreme passivity"],
        "communication_style": "Enthusiastic, bright, affectionate, and straightforward",
        "dating_intentions": "An uplifting, joyful partnership where we both shine brighter together",
        "tagline": "Engineering rocket valves by day, dancing salsa on Saturday nights."
    },
    {
        "name": "Fatima Zahra",
        "age": 30,
        "occupation": "Community Clinic Medical Director",
        "location": "Oakland, CA",
        "raw_input": "Family medicine doctor dedicated to community health clinics in the East Bay. Outside the clinic, I write poetry, cook spicy Moroccan tagines for friends, and hike the redwoods. I'm driven by justice, radical hospitality, and love for community. Looking for a partner whose heart is as big as their mind, who laughs freely, and who wants to make the world softer.",
        "values": ["Compassion", "Social justice", "Hospitality", "Vulnerability"],
        "hobbies": ["Moroccan cooking", "Poetry writing", "Redwood hiking", "Arabic calligraphy"],
        "interests": ["Public health policy", "Postcolonial literature", "Herbalism", "World cinema"],
        "needs": ["Deep emotional safety", "Shared ethical grounding", "Tenderness and laughter"],
        "dealbreakers": ["Self-absorption", "Cruelty", "Apathy towards injustice"],
        "communication_style": "Warm, articulate, emotionally deep, and radiant",
        "dating_intentions": "A deeply rooted, loving, purpose-driven life partnership",
        "tagline": "Family physician, poet, tagine chef, and redwood hiker."
    }
]


def seed_database_with_25_profiles(db: Session) -> int:
    """
    Seeds the SQLite DB with 25 pre-built synthetic profiles.
    Returns the count of new profiles added.
    """
    added = 0
    for candidate in SYNTHETIC_CANDIDATES:
        name = candidate["name"]
        # Check if already in DB
        existing = db.query(ProfileDB).filter(ProfileDB.name == name).first()
        if existing:
            continue

        analysis = ProfileAnalysis(
            name=name,
            age=candidate.get("age"),
            occupation=candidate.get("occupation"),
            location=candidate.get("location"),
            tagline=candidate.get("tagline"),
            needs=candidate.get("needs", []),
            hobbies=candidate.get("hobbies", []),
            interests=candidate.get("interests", []),
            values=candidate.get("values", []),
            communication_style=candidate.get("communication_style", "Warm and direct"),
            dealbreakers=candidate.get("dealbreakers", []),
            dating_intentions=candidate.get("dating_intentions", "Long-term partnership"),
            personality_type_hint=candidate.get("personality_type_hint")
        )

        avatar_url = f"https://api.dicebear.com/7.x/notionists/svg?seed={name.replace(' ', '')}"

        profile_db = ProfileDB(
            name=name,
            age=candidate.get("age"),
            occupation=candidate.get("occupation"),
            location=candidate.get("location"),
            source="synthetic",
            raw_input=candidate["raw_input"],
            avatar_url=avatar_url,
            analysis_json=json.dumps(analysis.model_dump())
        )
        db.add(profile_db)
        added += 1

    db.commit()
    logger.info(f"Seeded {added} synthetic profiles into the database.")
    return added
