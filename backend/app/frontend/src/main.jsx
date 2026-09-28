import React, {
    useEffect,
    useState
} from "react";

import {
    createRoot
} from "react-dom/client";

import {
    Home,
    PartyPopper,
    Gem,
    History as HistoryIcon,
    LogOut,
    Sparkles,
    Upload,
    Trash2,
    ExternalLink
} from "lucide-react";

import "./styles.css";


const API =
    import.meta.env.VITE_API_URL ||
    "http://localhost:8000/api";


const money = (value) =>
    new Intl.NumberFormat(
        "en-IN",
        {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 0
        }
    ).format(value || 0);


async function api(
    path,
    options = {}
) {

    const token =
        localStorage.getItem("token");

    const headers =
        new Headers(
            options.headers || {}
        );

    if (token) {

        headers.set(
            "Authorization",
            `Bearer ${token}`
        );
    }

    if (
        options.body &&
        !(options.body instanceof FormData)
    ) {

        headers.set(
            "Content-Type",
            "application/json"
        );
    }

    const response = await fetch(
        API + path,
        {
            ...options,
            headers
        }
    );

    const data =
        await response
            .json()
            .catch(
                () => ({
                    detail:
                        "Server error"
                })
            );

    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Request failed"
        );
    }

    return data;
}


// =====================================================
// AUTH
// =====================================================

function Auth({
    onLogin
}) {

    const [
        register,
        setRegister
    ] = useState(false);

    const [
        name,
        setName
    ] = useState("");

    const [
        email,
        setEmail
    ] = useState("");

    const [
        password,
        setPassword
    ] = useState("");

    const [
        error,
        setError
    ] = useState("");


    async function submit(event) {

        event.preventDefault();

        setError("");

        try {

            const data =
                await api(
                    register
                        ? "/auth/register"
                        : "/auth/login",
                    {
                        method: "POST",

                        body:
                            JSON.stringify(
                                register
                                    ? {
                                        name,
                                        email,
                                        password
                                    }
                                    : {
                                        email,
                                        password
                                    }
                            )
                    }
                );

            localStorage.setItem(
                "token",
                data.access_token
            );

            onLogin(data.user);

        } catch (error) {

            setError(
                error.message
            );
        }
    }


    return (
        <div className="auth">

            <div className="auth-card">

                <div className="logo">

                    <Sparkles />

                    PocketSmart AI

                </div>


                <h1>

                    {register
                        ? "Create your account"
                        : "Welcome back"}

                </h1>


                <p>
                    AI-powered budget planning
                    for everyday needs.
                </p>


                <form
                    onSubmit={submit}
                >

                    {register && (

                        <input
                            placeholder="Name"
                            value={name}
                            onChange={(event) =>
                                setName(
                                    event.target.value
                                )
                            }
                            required
                        />

                    )}


                    <input
                        type="email"
                        placeholder="Email"
                        value={email}
                        onChange={(event) =>
                            setEmail(
                                event.target.value
                            )
                        }
                        required
                    />


                    <input
                        type="password"
                        placeholder="Password (6+ characters)"
                        value={password}
                        onChange={(event) =>
                            setPassword(
                                event.target.value
                            )
                        }
                        required
                        minLength="6"
                    />


                    {error && (

                        <div className="error">

                            {error}

                        </div>

                    )}


                    <button
                        className="primary"
                    >

                        {register
                            ? "Create account"
                            : "Sign in"}

                    </button>

                </form>


                <button
                    className="link"
                    onClick={() =>
                        setRegister(
                            !register
                        )
                    }
                >

                    {register
                        ? "Already have an account? Sign in"
                        : "New here? Create an account"}

                </button>

            </div>

        </div>
    );
}


// =====================================================
// PLANNER
// =====================================================

function Planner({
    type,
    onResult
}) {

    const plannerInfo = {

        home: {
            title:
                "Home Interior Budget Planner",

            icon: <Home />,

            desc:
                "Plan rooms, lighting and furniture within your budget."
        },

        party: {
            title:
                "Party Budget Planner",

            icon: <PartyPopper />,

            desc:
                "Allocate your event budget across practical needs."
        },

        jewelry: {
            title:
                "Jewelry Budget Planner",

            icon: <Gem />,

            desc:
                "Find occasion-friendly jewelry ideas within your budget."
        }

    }[type];


    const [
        form,
        setForm
    ] = useState({

        total_budget: "",

        num_lights: 2,

        num_fans: 1,

        num_furniture: 1,

        num_dining_tables: 0,

        has_living_room: true,

        has_kitchen: false,

        has_bedroom: false,

        party_type: "Birthday",

        num_guests: 10,

        venue_type: "Community hall",

        needs_catering: true,

        needs_decoration: true,

        needs_entertainment: false,

        occasion: "Birthday",

        preferences: "",

        additional_requirements: ""
    });


    const [
        image,
        setImage
    ] = useState(null);


    const [
        loading,
        setLoading
    ] = useState(false);


    const [
        error,
        setError
    ] = useState("");


    function set(
        key,
        value
    ) {

        setForm({
            ...form,
            [key]: value
        });
    }


    async function submit(event) {

        event.preventDefault();

        setLoading(true);

        setError("");


        try {

            let data;


            // ---------------------------------------
            // JEWELRY
            // ---------------------------------------

            if (type === "jewelry") {

                const formData =
                    new FormData();

                formData.append(
                    "total_budget",
                    form.total_budget
                );

                formData.append(
                    "occasion",
                    form.occasion
                );

                formData.append(
                    "preferences",
                    form.preferences
                );

                if (image) {

                    formData.append(
                        "image",
                        image
                    );
                }


                data =
                    await api(
                        "/planners/jewelry",
                        {
                            method: "POST",
                            body: formData
                        }
                    );

            }

            // ---------------------------------------
            // HOME / PARTY
            // ---------------------------------------

            else {

                const payload =
                    type === "home"

                        ? {
                            ...form,

                            total_budget:
                                Number(
                                    form.total_budget
                                )
                        }

                        : {
                            ...form,

                            total_budget:
                                Number(
                                    form.total_budget
                                ),

                            num_guests:
                                Number(
                                    form.num_guests
                                )
                        };


                data =
                    await api(
                        `/planners/${type}`,
                        {
                            method: "POST",

                            body:
                                JSON.stringify(
                                    payload
                                )
                        }
                    );
            }


            onResult(data);

        } catch (error) {

            setError(
                error.message
            );

        } finally {

            setLoading(false);
        }
    }


    return (

        <section>

            <div className="section-head">

                <div className="iconbox">

                    {plannerInfo.icon}

                </div>

                <div>

                    <h2>
                        {plannerInfo.title}
                    </h2>

                    <p>
                        {plannerInfo.desc}
                    </p>

                </div>

            </div>


            <form
                className="planner"
                onSubmit={submit}
            >

                <label>

                    Total budget (INR)

                    <input
                        type="number"
                        min="1"
                        value={form.total_budget}
                        onChange={(event) =>
                            set(
                                "total_budget",
                                event.target.value
                            )
                        }
                        required
                    />

                </label>


                {/* HOME */}

                {type === "home" && (

                    <>

                        <div className="grid3">

                            <label>

                                Lights

                                <input
                                    type="number"
                                    min="0"
                                    value={form.num_lights}
                                    onChange={(event) =>
                                        set(
                                            "num_lights",
                                            Number(
                                                event.target.value
                                            )
                                        )
                                    }
                                />

                            </label>


                            <label>

                                Ceiling fans

                                <input
                                    type="number"
                                    min="0"
                                    value={form.num_fans}
                                    onChange={(event) =>
                                        set(
                                            "num_fans",
                                            Number(
                                                event.target.value
                                            )
                                        )
                                    }
                                />

                            </label>


                            <label>

                                Furniture pieces

                                <input
                                    type="number"
                                    min="0"
                                    value={
                                        form.num_furniture
                                    }
                                    onChange={(event) =>
                                        set(
                                            "num_furniture",
                                            Number(
                                                event.target.value
                                            )
                                        )
                                    }
                                />

                            </label>

                        </div>


                        <label>

                            Dining tables

                            <input
                                type="number"
                                min="0"
                                value={
                                    form.num_dining_tables
                                }
                                onChange={(event) =>
                                    set(
                                        "num_dining_tables",
                                        Number(
                                            event.target.value
                                        )
                                    )
                                }
                            />

                        </label>


                        <div className="checks">

                            <label>

                                <input
                                    type="checkbox"
                                    checked={
                                        form.has_living_room
                                    }
                                    onChange={(event) =>
                                        set(
                                            "has_living_room",
                                            event.target.checked
                                        )
                                    }
                                />

                                Living room

                            </label>


                            <label>

                                <input
                                    type="checkbox"
                                    checked={
                                        form.has_kitchen
                                    }
                                    onChange={(event) =>
                                        set(
                                            "has_kitchen",
                                            event.target.checked
                                        )
                                    }
                                />

                                Kitchen

                            </label>


                            <label>

                                <input
                                    type="checkbox"
                                    checked={
                                        form.has_bedroom
                                    }
                                    onChange={(event) =>
                                        set(
                                            "has_bedroom",
                                            event.target.checked
                                        )
                                    }
                                />

                                Bedroom

                            </label>

                        </div>

                    </>

                )}


                {/* PARTY */}

                {type === "party" && (

                    <>

                        <div className="grid2">

                            <label>

                                Party type

                                <input
                                    value={
                                        form.party_type
                                    }
                                    onChange={(event) =>
                                        set(
                                            "party_type",
                                            event.target.value
                                        )
                                    }
                                />

                            </label>


                            <label>

                                Guests

                                <input
                                    type="number"
                                    min="1"
                                    value={
                                        form.num_guests
                                    }
                                    onChange={(event) =>
                                        set(
                                            "num_guests",
                                            Number(
                                                event.target.value
                                            )
                                        )
                                    }
                                />

                            </label>

                        </div>


                        <label>

                            Venue type

                            <input
                                value={
                                    form.venue_type
                                }
                                onChange={(event) =>
                                    set(
                                        "venue_type",
                                        event.target.value
                                    )
                                }
                            />

                        </label>


                        <div className="checks">

                            <label>

                                <input
                                    type="checkbox"
                                    checked={
                                        form.needs_catering
                                    }
                                    onChange={(event) =>
                                        set(
                                            "needs_catering",
                                            event.target.checked
                                        )
                                    }
                                />

                                Catering

                            </label>


                            <label>

                                <input
                                    type="checkbox"
                                    checked={
                                        form.needs_decoration
                                    }
                                    onChange={(event) =>
                                        set(
                                            "needs_decoration",
                                            event.target.checked
                                        )
                                    }
                                />

                                Decoration

                            </label>


                            <label>

                                <input
                                    type="checkbox"
                                    checked={
                                        form.needs_entertainment
                                    }
                                    onChange={(event) =>
                                        set(
                                            "needs_entertainment",
                                            event.target.checked
                                        )
                                    }
                                />

                                Entertainment

                            </label>

                        </div>

                    </>

                )}


                {/* JEWELRY */}

                {type === "jewelry" && (

                    <>

                        <label>

                            Occasion

                            <input
                                value={
                                    form.occasion
                                }
                                onChange={(event) =>
                                    set(
                                        "occasion",
                                        event.target.value
                                    )
                                }
                                required
                            />

                        </label>


                        <label>

                            Style preferences

                            <textarea
                                value={
                                    form.preferences
                                }
                                onChange={(event) =>
                                    set(
                                        "preferences",
                                        event.target.value
                                    )
                                }
                                placeholder="Example: simple, traditional, lightweight"
                            />

                        </label>


                        <label className="upload">

                            <Upload />

                            Outfit image (optional)

                            <input
                                type="file"
                                accept="image/png,image/jpeg,image/webp"
                                onChange={(event) =>
                                    setImage(
                                        event.target.files?.[0] ||
                                        null
                                    )
                                }
                            />

                            {image && (
                                <span>
                                    {image.name}
                                </span>
                            )}

                        </label>

                    </>

                )}


                <label>

                    Additional requirements

                    <textarea
                        value={
                            form.additional_requirements
                        }
                        onChange={(event) =>
                            set(
                                "additional_requirements",
                                event.target.value
                            )
                        }
                        placeholder="Anything else the AI should consider?"
                    />

                </label>


                {error && (

                    <div className="error">

                        {error}

                    </div>

                )}


                <button
                    className="primary"
                    disabled={loading}
                >

                    <Sparkles />

                    {loading
                        ? "Generating..."
                        : "Generate Recommendations"}

                </button>

            </form>

        </section>
    );
}


// =====================================================
// RESULT
// =====================================================

function Result({
    data
}) {

    return (

        <div className="result">

            <div className="result-top">

                <div>

                    <span className="eyebrow">

                        Personalized Budget Plan

                    </span>

                    <h2>

                        {money(
                            data.total_budget
                        )}

                    </h2>

                </div>


                <div className="remaining">

                    Remaining

                    <br />

                    <b>
                        {money(
                            data.remaining_budget
                        )}
                    </b>

                </div>

            </div>


            {data.outfit_analysis && (

                <div className="note">

                    <b>
                        Outfit analysis:
                    </b>{" "}

                    {data.outfit_analysis.colors?.join(
                        ", "
                    )}

                    {" · "}

                    {data.outfit_analysis.style || ""}

                </div>

            )}


            {data.budget_breakdown.map(
                (category, index) => (

                    <div
                        className="category"
                        key={index}
                    >

                        <div className="cat-head">

                            <h3>
                                {category.category}
                            </h3>

                            <b>
                                {money(
                                    category.allocation
                                )}
                            </b>

                        </div>


                        {category.items.map(
                            (item, itemIndex) => (

                                <div
                                    className="item"
                                    key={itemIndex}
                                >

                                    <div>

                                        <b>
                                            {item.name}
                                        </b>

                                        <p>
                                            {item.description}
                                        </p>

                                        <small>

                                            {money(
                                                item.estimated_price
                                            )}

                                            {" × "}

                                            {item.quantity}

                                        </small>

                                    </div>


                                    <div className="links">

                                        {Object.entries(
                                            item.shopping_links || {}
                                        ).map(
                                            ([platform, url]) => (

                                                <a
                                                    href={url}
                                                    target="_blank"
                                                    rel="noreferrer"
                                                    key={platform}
                                                >

                                                    {platform}

                                                    <ExternalLink
                                                        size={13}
                                                    />

                                                </a>

                                            )
                                        )}

                                    </div>

                                </div>

                            )
                        )}

                    </div>

                )
            )}


            {
                (
                    data.additional_suggestions
                        ?.length > 0

                    ||

                    data.styling_tips
                        ?.length > 0
                ) && (

                    <div className="tips">

                        <h3>
                            Tips
                        </h3>

                        {[
                            ...(data.additional_suggestions || []),
                            ...(data.styling_tips || [])
                        ].map(
                            (tip, index) => (

                                <p key={index}>
                                    • {tip}
                                </p>

                            )
                        )}

                    </div>

                )
            }

        </div>
    );
}


// =====================================================
// HISTORY
// =====================================================

function History() {

    const [
        rows,
        setRows
    ] = useState([]);


    useEffect(() => {

        api("/history")
            .then(setRows)
            .catch(() => {});

    }, []);


    async function deleteRecord(
        id
    ) {

        try {

            await api(
                `/history/${id}`,
                {
                    method: "DELETE"
                }
            );

            setRows(
                rows.filter(
                    row => row.id !== id
                )
            );

        } catch (error) {

            alert(
                error.message
            );
        }
    }


    return (

        <section>

            <div className="section-head">

                <div className="iconbox">

                    <HistoryIcon />

                </div>

                <div>

                    <h2>
                        Recommendation History
                    </h2>

                    <p>
                        View your previous budget plans.
                    </p>

                </div>

            </div>


            {rows.length === 0 ? (

                <div className="empty">

                    No recommendations yet.

                </div>

            ) : (

                <div className="history">

                    {rows.map(
                        row => (

                            <div
                                className="history-row"
                                key={row.id}
                            >

                                <div>

                                    <b>
                                        {row.planner}
                                        {" "}
                                        budget plan
                                    </b>

                                    <p>

                                        {new Date(
                                            row.created_at
                                        ).toLocaleString()}

                                        {" · Budget "}

                                        {money(
                                            row.total_budget
                                        )}

                                    </p>

                                </div>


                                <button
                                    className="icon-btn"
                                    onClick={() =>
                                        deleteRecord(
                                            row.id
                                        )
                                    }
                                    title="Delete"
                                >

                                    <Trash2 />

                                </button>

                            </div>

                        )
                    )}

                </div>

            )}

        </section>
    );
}


// =====================================================
// APP
// =====================================================

function App() {

    const [
        user,
        setUser
    ] = useState(null);


    const [
        tab,
        setTab
    ] = useState("home");


    const [
        result,
        setResult
    ] = useState(null);


    useEffect(() => {

        const token =
            localStorage.getItem(
                "token"
            );

        if (!token) {
            return;
        }

        api("/auth/me")
            .then(setUser)
            .catch(() => {

                localStorage.removeItem(
                    "token"
                );

            });

    }, []);


    if (!user) {

        return (
            <Auth
                onLogin={setUser}
            />
        );
    }


    function logout() {

        localStorage.removeItem(
            "token"
        );

        setUser(null);
    }


    const navigation = [

        [
            "home",
            "Home Planner",
            Home
        ],

        [
            "party",
            "Party Planner",
            PartyPopper
        ],

        [
            "jewelry",
            "Jewelry Planner",
            Gem
        ],

        [
            "history",
            "History",
            HistoryIcon
        ]

    ];


    return (

        <div className="app">

            <header>

                <div className="brand">

                    <Sparkles />

                    PocketSmart AI

                </div>


                <nav>

                    {navigation.map(
                        ([key, title, Icon]) => (

                            <button
                                key={key}
                                className={
                                    tab === key
                                        ? "active"
                                        : ""
                                }
                                onClick={() => {

                                    setTab(key);

                                    setResult(null);

                                }}
                            >

                                <Icon
                                    size={17}
                                />

                                {title}

                            </button>

                        )
                    )}

                </nav>


                <div className="user">

                    Hi, {user.name}

                    <button
                        onClick={logout}
                    >

                        <LogOut
                            size={16}
                        />

                    </button>

                </div>

            </header>


            <main>

                <div className="hero">

                    <span>
                        SMART BUDGETING
                    </span>

                    <h1>
                        Plan smarter.
                        Spend with purpose.
                    </h1>

                    <p>
                        Personalized recommendations
                        for home interiors, parties,
                        and jewelry — built around
                        your budget.
                    </p>

                </div>


                {tab === "history" ? (

                    <History />

                ) : (

                    <div className="workspace">

                        <Planner
                            type={tab}
                            onResult={setResult}
                        />

                        {result && (
                            <Result
                                data={result}
                            />
                        )}

                    </div>

                )}

            </main>

        </div>
    );
}


createRoot(
    document.getElementById("root")
).render(
    <App />
);