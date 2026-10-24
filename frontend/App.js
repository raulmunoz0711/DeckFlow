import { CameraView, useCameraPermissions } from "expo-camera";
import { StatusBar } from "expo-status-bar";
import { useEffect, useRef, useState } from "react";
import { ActivityIndicator, Image, ImageBackground, Modal, Platform, Pressable, SafeAreaView, ScrollView, StyleSheet, Text, TextInput, View } from "react-native";

const WEB_HOST = Platform.OS === "web" && typeof window !== "undefined" ? window.location.hostname : "localhost";
const API_URL = Platform.OS === "web" ? window.location.origin : (process.env.EXPO_PUBLIC_API_URL || "http://localhost:8000");
const sampleCards = {
  "charizard-ex-223": { Front: "/sample_data/charizard-front.png", Back: "/sample_data/card-back.png" },
  "pikachu-160": { Front: "/sample_data/pikachu-front.png", Back: "/sample_data/card-back.png" },
  "umbreon-vmax-215": { Front: "/sample_data/umbreon-front.png", Back: "/sample_data/card-back.png" },
};

function Button({ children, onPress, secondary, disabled }) {
  return <Pressable accessibilityRole="button" disabled={disabled} onPress={onPress} style={({ pressed }) => [s.button, secondary && s.secondaryButton, (pressed || disabled) && s.dim]}><Text style={[s.buttonText, secondary && s.secondaryText]}>{children}</Text></Pressable>;
}

function Camera({ side, close, captured }) {
  const ref = useRef(null);
  const [permission, requestPermission] = useCameraPermissions();
  const [busy, setBusy] = useState(false);
  async function snap() {
    if (!ref.current) return;
    setBusy(true);
    try {
      const photo = await ref.current.takePictureAsync({ quality: .9, base64: Platform.OS === "web" });
      captured({ uri: photo.uri, name: `card_${side.toLowerCase()}_${Date.now()}.jpg`, type: "image/jpeg" });
    } finally { setBusy(false); }
  }
  return <Modal visible animationType="slide" onRequestClose={close}><SafeAreaView style={s.cameraPage}>
    <View style={s.cameraHeader}><View><Text style={s.lightKicker}>LIVE CAMERA</Text><Text style={s.cameraTitle}>Capture card {side.toLowerCase()}</Text></View><Pressable onPress={close}><Text style={s.close}>Close</Text></Pressable></View>
    {!permission ? <ActivityIndicator color="#d9ff79" /> : !permission.granted ? <View style={s.permission}><Text style={s.permissionText}>DeckFlow needs camera permission to photograph the card.</Text><Button onPress={requestPermission}>Allow camera</Button></View> : <>
      <View style={s.cameraFrame}><CameraView ref={ref} style={StyleSheet.absoluteFill} facing="back" mode="picture" /><View pointerEvents="none" style={s.guideLayer}><View style={s.guide}><Text style={s.guideText}>ALIGN CARD HERE</Text></View></View></View>
      <Button onPress={snap} disabled={busy}>{busy ? "Capturing…" : `Capture ${side}`}</Button>
    </>}
  </SafeAreaView></Modal>;
}

function Photo({ side, photo, sample, open, useSample, rotate }) {
  return <View style={s.photo}><Text style={s.photoTitle}>{side}</Text><Image source={{ uri: photo?.previewUri || photo?.uri || sample }} style={s.cardImage} resizeMode="contain" /><Button onPress={open}>Scan {side.toLowerCase()}</Button>{photo ? <Button secondary onPress={rotate}>Rotate photo ↻</Button> : <Button secondary onPress={useSample}>Use demo image</Button>}<Text numberOfLines={2} style={s.small}>{photo?.scanning ? "Detecting and clipping card…" : photo?.boundaryDetected === false ? "Guide crop used—make sure only the card fills the outline" : photo?.name || "Demo image"}</Text></View>;
}

function Report({ data, selectCandidate }) {
  if (!data) return <View style={s.empty}><Text style={s.spark}>✦</Text><Text style={s.emptyTitle}>No report yet</Text><Text style={s.muted}>Capture both sides or use the sample, then analyze the card.</Text></View>;
  return <View style={s.report}>
    <View style={s.reportHead}><View style={s.identity}><Text style={s.kicker}>IDENTIFIED CARD</Text><Text style={s.cardName}>{data.card_name}</Text><Text style={s.muted}>{data.set_name} · {data.card_number}{"\n"}{data.variant}</Text></View><View style={s.grade}><Text style={s.gradeLabel}>ESTIMATED</Text><Text style={s.gradeValue}>{data.estimated_grade}</Text><Text style={s.gradeLabel}>Range {data.grade_range}</Text></View></View>
    <View style={s.stats}>{[["Condition", data.condition], ["Confidence", `${Math.round(data.confidence * 100)}%`], ["Centering", data.centering.split(" front")[0]]].map(([a,b]) => <View key={a} style={s.stat}><Text style={s.small}>{a}</Text><Text style={s.statValue}>{b}</Text></View>)}</View>
    <Text style={s.blockTitle}>Visible-defect review</Text>{data.defects.map(d => <View key={d.category} style={s.defect}><View style={[s.dot, d.severity === "none" && s.good]} /><View><Text style={s.defectTitle}>{d.category}</Text><Text style={s.small}>{d.result}</Text></View></View>)}
    <View style={s.stats}><View style={s.stat}><Text style={s.small}>Raw market estimate</Text><Text style={s.price}>${data.raw_market_price.toFixed(2)}</Text></View><View style={s.stat}><Text style={s.small}>Graded estimate</Text><Text style={s.price}>${data.graded_market_price.toFixed(2)}</Text></View></View>
    {data.card_candidates?.length > 1 ? <View style={s.candidateBox}><Text style={s.blockTitle}>Possible card matches</Text><Text style={s.small}>Not the right card? Pick another match to load its market price.</Text>{data.card_candidates.map((candidate, index) => {
      const selected = candidate.card_name === data.card_name && candidate.card_number === data.card_number && candidate.set_name === data.set_name;
      return <Pressable key={`${candidate.justtcg_id || candidate.card_number}-${index}`} onPress={() => selectCandidate(candidate)} style={[s.candidate, selected && s.selectedCandidate]}><View style={{flex:1}}><Text style={s.choiceTitle}>{candidate.card_name}</Text><Text style={s.small}>{candidate.set_name} · {candidate.card_number} · {candidate.variant}</Text></View><Text style={s.selectText}>{selected ? "SELECTED" : "VIEW PRICE"}</Text></Pressable>;
    })}</View> : null}
    <View style={s.note}><Text style={s.noteTitle}>Recommendation</Text><Text style={s.noteText}>{data.recommendation}</Text></View><View style={[s.note, s.greenNote]}><Text style={s.noteTitle}>Selling window</Text><Text style={s.noteText}>{data.selling_window}</Text></View>
    <Text style={s.source}>Identification: {data.identification_mode}{"\n"}Pricing: {data.pricing_source}</Text>
  </View>;
}

function MobileUpload({ sessionId }) {
  const [front, setFront] = useState(null);
  const [back, setBack] = useState(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [pickerVersion, setPickerVersion] = useState(0);
  async function send() {
    if (!front || !back) return setMessage("Take both the front and back pictures first.");
    setBusy(true); setMessage("");
    try {
      const form = new FormData(); form.append("front", front, front.name); form.append("back", back, back.name);
      const response = await fetch(`${API_URL}/api/mobile-sessions/${sessionId}/upload`, { method:"POST", body:form });
      const body = await response.json(); if (!response.ok) throw new Error(body.detail || "Upload failed.");
      setMessage(`✓ Card ${body.upload_count} sent. You can photograph another card here without scanning the QR again.`);
      setFront(null); setBack(null); setPickerVersion(value => value + 1);
    } catch (e) { setMessage(e.message || "Could not reach the laptop."); } finally { setBusy(false); }
  }
  const picker = (label, file, setFile) => <View style={s.mobilePicker}><Text style={s.photoTitle}>{label}</Text><input key={`${label}-${pickerVersion}`} type="file" accept="image/*" capture="environment" onChange={e => setFile(e.target.files?.[0] || null)} style={{fontSize:16,width:"100%"}} />{file ? <Text style={s.mobileReady}>✓ {file.name}</Text> : <Text style={s.muted}>Use the rear camera and keep all four card edges visible.</Text>}</View>;
  return <SafeAreaView style={s.mobilePage}><StatusBar style="dark" /><View style={s.mobileCard}><View style={s.logo}><Text style={s.logoText}>DF</Text></View><Text style={s.mobileTitle}>Send card to DeckFlow</Text><Text style={s.muted}>Photograph the card flat on a plain dark surface. These pictures will appear automatically on the laptop.</Text>{picker("1. Card front",front,setFront)}{picker("2. Card back",back,setBack)}<Button onPress={send} disabled={busy}>{busy ? "Sending…" : "Send to laptop"}</Button>{message ? <Text style={message.startsWith("✓") ? s.mobileSuccess : s.error}>{message}</Text> : null}</View></SafeAreaView>;
}

function LoadingRunner() {
  const [step, setStep] = useState(0);
  useEffect(() => { const timer = setInterval(() => setStep(value => (value + 1) % 12), 120); return () => clearInterval(timer); }, []);
  return <View style={s.loadingScene}><View style={s.loadingTrack}><Text style={[s.runner, {marginLeft:`${step * 7}%`}]}>{step % 2 ? "⚡ ◒" : "⚡ ◓"}</Text></View><Text style={s.loadingTitle}>Deck buddy is checking the edges…</Text><Text style={s.muted}>Comparing centering, corners, surface and market matches.</Text></View>;
}

function DesktopApp() {
  const [photos, setPhotos] = useState({ Front: null, Back: null });
  const [cameraSide, setCameraSide] = useState(null);
  const [cardId, setCardId] = useState("charizard-ex-223");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [cardHint, setCardHint] = useState("");
  const [phoneSession, setPhoneSession] = useState(null);
  const lastPhoneUpload = useRef(0);
  const qrStarting = useRef(false);
  const [publicUrl, setPublicUrl] = useState("");
  const samples = sampleCards[cardId] || sampleCards["charizard-ex-223"];
  useEffect(() => { refreshHistory(); }, []);
  useEffect(() => {
    if (Platform.OS !== "web" || phoneSession || qrStarting.current) return;
    let stopped = false;
    const discover = async () => {
      try {
        const response = await fetch(`${API_URL}/api/public-url`);
        if (!response.ok) return;
        const body = await response.json();
        if (!stopped && body.url) {
          setPublicUrl(body.url);
          qrStarting.current = true;
          await createPhoneSession(body.url);
        }
      } catch {}
    };
    discover();
    const timer = setInterval(discover, 2000);
    return () => { stopped = true; clearInterval(timer); };
  }, [phoneSession]);
  useEffect(() => {
    if (!phoneSession?.session_id) return;
    const timer = setInterval(async () => {
      try {
        const response = await fetch(`${API_URL}/api/mobile-sessions/${phoneSession.session_id}`);
        if (!response.ok) return;
        const status = await response.json(); setPhoneSession(old => ({...old,...status,qr_data_url:status.qr_data_url || old?.qr_data_url}));
        if ((status.upload_count || 0) > lastPhoneUpload.current) {
          lastPhoneUpload.current = status.upload_count;
          await receivePhonePhotos(phoneSession.session_id);
        }
      } catch {}
    }, 1500);
    return () => clearInterval(timer);
  }, [phoneSession?.session_id]);
  async function refreshHistory() { try { const r = await fetch(`${API_URL}/api/assessments`); if (r.ok) setHistory(await r.json()); } catch {} }
  async function appendPhoto(form, key, photo, sample) {
    if (Platform.OS === "web") { const response = await fetch(photo?.uri || sample); form.append(key, await response.blob(), photo?.name || `sample_${key}.svg`); }
    else if (photo) form.append(key, { uri: photo.uri, name: photo.name, type: photo.type });
    else throw new Error(`Capture the card ${key} before analyzing on a phone.`);
  }
  async function clipPhoto(side, photo, requestedRotation = photo.rotation || 0) {
    const nextPhoto = { ...photo, rotation: requestedRotation, scanning: true };
    setPhotos(old => ({ ...old, [side]: nextPhoto }));
    try {
      const form = new FormData();
      if (Platform.OS === "web") {
        const response = await fetch(photo.uri);
        form.append("image", await response.blob(), photo.name);
      } else form.append("image", { uri: photo.uri, name: photo.name, type: photo.type });
      form.append("rotation", String(requestedRotation));
      const response = await fetch(`${API_URL}/api/crop`, { method: "POST", body: form });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail || "Card clipping failed.");
      setPhotos(old => ({ ...old, [side]: { ...photo, rotation: requestedRotation, previewUri: body.preview, boundaryDetected: body.boundary_detected, scanning: false } }));
    } catch (e) {
      setPhotos(old => ({ ...old, [side]: { ...photo, boundaryDetected: false, scanning: false } }));
      setError(e.message || "Could not clip the card image.");
    }
  }
  async function createPhoneSession(baseUrl = publicUrl) {
    setError("");
    try {
      if (!baseUrl) throw new Error("The secure phone link is still starting.");
      const form = new FormData(); form.append("public_base_url", baseUrl);
      const response = await fetch(`${API_URL}/api/mobile-sessions`, {method:"POST",body:form});
      const body = await response.json(); if (!response.ok) throw new Error(body.detail || "Could not create QR session.");
      lastPhoneUpload.current = 0;
      setPhoneSession(body);
    } catch (e) { qrStarting.current = false; setError(e.message); }
  }
  async function receivePhonePhotos(sessionId) {
    const [frontResponse, backResponse] = await Promise.all([fetch(`${API_URL}/api/mobile-sessions/${sessionId}/image/front`), fetch(`${API_URL}/api/mobile-sessions/${sessionId}/image/back`)]);
    const frontPhoto = {uri:URL.createObjectURL(await frontResponse.blob()),name:"Phone card front.jpg",type:"image/jpeg",rotation:0};
    const backPhoto = {uri:URL.createObjectURL(await backResponse.blob()),name:"Phone card back.jpg",type:"image/jpeg",rotation:0};
    setCardHint(""); setResult(null);
    await Promise.all([clipPhoto("Front",frontPhoto),clipPhoto("Back",backPhoto)]);
  }
  async function analyze() {
    setLoading(true); setError(""); setResult(null);
    try {
      const form = new FormData(); await appendPhoto(form, "front", photos.Front, samples.Front); await appendPhoto(form, "back", photos.Back, samples.Back); form.append("card_id", cardId); form.append("card_hint", cardHint); form.append("front_rotation", String(photos.Front?.rotation || 0)); form.append("back_rotation", String(photos.Back?.rotation || 0));
      const response = await fetch(`${API_URL}/api/assessments`, { method: "POST", body: form }); const body = await response.json(); if (!response.ok) throw new Error(body.detail || "Analysis failed.");
      setResult(body);
      setPhotos({ Front: { uri: body.front_preview, name: "Auto-cropped front" }, Back: { uri: body.back_preview, name: "Auto-cropped back" } });
      await refreshHistory();
    } catch (e) { setError(e.message || "Cannot reach the DeckFlow API."); } finally { setLoading(false); }
  }
  async function selectCandidate(candidate) {
    if (!result) return;
    setError("");
    try {
      const response = await fetch(`${API_URL}/api/candidate-price`, {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({...candidate,estimated_grade:result.estimated_grade,condition:result.condition})});
      const priced = await response.json(); if (!response.ok) throw new Error(priced.detail || "Could not load that card's price.");
      setResult(old => ({...old,...priced}));
    } catch (e) { setError(e.message || "Could not load that card's price."); }
  }
  return <ImageBackground source={{ uri: "/sample_data/library-background.webp" }} style={s.background} imageStyle={s.backgroundImage} resizeMode="cover"><SafeAreaView style={s.safe}><StatusBar style="dark" />{cameraSide && <Camera side={cameraSide} close={() => setCameraSide(null)} captured={p => { const side = cameraSide; if (side === "Front") setCardHint(""); setCameraSide(null); clipPhoto(side, p); }} />}
    <ScrollView contentContainerStyle={s.page}>
      <View style={s.header}><View style={s.brand}><View style={s.logo}><Text style={s.logoText}>DF</Text></View><View><Text style={s.brandTitle}>DeckFlow</Text><Text style={s.small}>React Native card pre-grading</Text></View></View><View style={s.badge}><Text style={s.badgeText}>CPSC 490 Demo</Text></View></View>
      <View style={s.hero}><Text style={s.kicker}>BUILT BY COLLECTORS, FOR COLLECTORS</Text><Text style={s.heroTitle}>Give your card a careful first look.</Text><Text style={s.heroCopy}>We built DeckFlow to answer the question we always ask before sending a card out: is this one worth grading? Snap both sides, check the match, and use the estimate as a practical second opinion.</Text><Text style={s.handNote}>↳ Tip from our team: soft daylight and a dark desk give the cleanest scan.</Text></View>
      <View style={s.grid}><View style={s.panel}><Text style={s.step}>01 · AI CARD SCAN</Text><Text style={s.panelTitle}>Grade one Pokémon card</Text><Text style={s.muted}>Scan both sides. DeckFlow clips the card from the background, reads its identity with OCR, and searches JustTCG automatically.</Text>
        <TextInput value={cardHint} onChangeText={setCardHint} placeholder="Optional: card name or number (example: 160/159)" style={s.input} />
        <View style={s.aiStatus}><View style={s.liveDot} /><View><Text style={s.aiLive}>AI LIVE</Text><Text style={s.small}>Card detection, OCR identification and visual pre-grading are active</Text></View></View>
        <View style={s.phoneBox}><Text style={s.phoneTitle}>Use your phone camera</Text><Text style={s.small}>Scan once, then keep this page open. The same QR accepts as many card pairs as you want—no IP address or Wi-Fi setup needed.</Text>{phoneSession ? <View style={s.qrRow}><Image source={{uri:phoneSession.qr_data_url}} style={s.qrImage} /><View style={{flex:1}}><Text style={s.phoneState}>{phoneSession.upload_count ? `✓ ${phoneSession.upload_count} card${phoneSession.upload_count === 1 ? "" : "s"} received · ready for another` : "● Ready for your first card"}</Text><Text style={s.small}>Secure phone link active</Text></View></View> : <View style={s.qrLoading}><ActivityIndicator color="#173c2e" /><Text style={s.small}>Creating secure phone link…</Text></View>}</View>
        <View style={s.photos}><Photo side="Front" photo={photos.Front} sample={samples.Front} open={() => setCameraSide("Front")} useSample={() => { setCardHint("Charizard ex 223/197"); clipPhoto("Front", {uri:samples.Front,name:"Demo front",type:"image/png",rotation:0}); }} rotate={() => clipPhoto("Front", photos.Front, (photos.Front.rotation + 1) % 4)} /><Photo side="Back" photo={photos.Back} sample={samples.Back} open={() => setCameraSide("Back")} useSample={() => clipPhoto("Back", {uri:samples.Back,name:"Demo back",type:"image/png",rotation:0})} rotate={() => clipPhoto("Back", photos.Back, (photos.Back.rotation + 1) % 4)} /></View>
        <Button onPress={analyze} disabled={loading}>{loading ? "Analyzing…" : "Analyze card"}</Button>{error ? <Text accessibilityRole="alert" style={s.error}>{error}</Text> : null}<Text style={s.disclaimer}>Unofficial estimate only. DeckFlow does not replace professional grading.</Text>
      </View><View style={s.panel}><Text style={s.step}>02 · ASSESSMENT</Text><Text style={s.panelTitle}>{result ? `Report ${result.assessment_id}` : "Assessment report"}</Text>{loading ? <LoadingRunner /> : <Report data={result} selectCandidate={selectCandidate} />}</View></View>
      <View style={s.panel}><Text style={s.step}>03 · HISTORY</Text><Text style={s.panelTitle}>Recent assessments</Text>{history.length ? <View style={s.history}>{history.map(x => <Pressable key={x.created_at} onPress={() => setResult(x)} style={s.historyItem}><View><Text style={s.choiceTitle}>{x.card_name}</Text><Text style={s.small}>{x.set_name} · {x.card_number}</Text></View><View style={s.historyRight}><Text style={s.historyGrade}>{x.estimated_grade}</Text><Text style={s.small}>${x.raw_market_price.toFixed(2)} raw</Text></View></Pressable>)}</View> : <Text style={s.muted}>No assessments saved in this session.</Text>}</View>
      <Text style={s.attribution}>Background artwork: “Let's Find Pokémon! – Library” by Kazunori Aihara · Classroom prototype use</Text>
    </ScrollView></SafeAreaView></ImageBackground>;
}

const s = StyleSheet.create({background:{flex:1,backgroundColor:"#f3ead8"},backgroundImage:{opacity:.34},safe:{flex:1,backgroundColor:"rgba(250,247,239,.72)"},page:{width:"100%",maxWidth:1220,alignSelf:"center",padding:24,gap:20},header:{flexDirection:"row",justifyContent:"space-between",alignItems:"center"},brand:{flexDirection:"row",alignItems:"center",gap:12},logo:{width:48,height:48,borderRadius:12,backgroundColor:"#173c2e",alignItems:"center",justifyContent:"center"},logoText:{color:"white",fontWeight:"800"},brandTitle:{fontSize:20,fontWeight:"800",color:"#18201d"},badge:{backgroundColor:"rgba(223,232,223,.94)",paddingVertical:8,paddingHorizontal:12,borderRadius:30},badgeText:{color:"#24533e",fontSize:12,fontWeight:"800"},hero:{maxWidth:760,paddingVertical:26},kicker:{color:"#a75d39",letterSpacing:2,fontSize:11,fontWeight:"800",marginBottom:10},heroTitle:{fontSize:46,lineHeight:49,fontWeight:"700",color:"#18201d",marginBottom:14},heroCopy:{fontSize:16,lineHeight:25,color:"#4f5853"},grid:{flexDirection:"row",gap:20,alignItems:"flex-start",flexWrap:"wrap"},panel:{backgroundColor:"rgba(255,255,255,.94)",borderRadius:18,padding:24,minWidth:320,flexGrow:1,flexBasis:480,boxShadow:"0 12px 38px rgba(36,57,47,.14)"},step:{color:"#a75d39",fontSize:11,fontWeight:"800",letterSpacing:1},panelTitle:{fontSize:19,fontWeight:"800",color:"#18201d",marginVertical:6},muted:{color:"#747d78",fontSize:13,lineHeight:19},small:{color:"#7c8580",fontSize:11},input:{borderWidth:1,borderColor:"#bfcac3",backgroundColor:"white",borderRadius:10,padding:12,marginTop:14,color:"#18201d"},sampleLabel:{fontSize:9,fontWeight:"800",letterSpacing:1,color:"#858b87",marginTop:13},sampleChoices:{flexDirection:"row",gap:6,flexWrap:"wrap",marginVertical:8},sampleChoice:{borderWidth:1,borderColor:"#dfe4df",borderRadius:20,paddingVertical:7,paddingHorizontal:10},activeChoice:{backgroundColor:"#eaf2ed",borderColor:"#35664f"},choiceTitle:{fontWeight:"800",color:"#26332d"},photos:{flexDirection:"row",gap:12,flexWrap:"wrap"},photo:{flex:1,minWidth:175,borderWidth:1,borderColor:"#dfe4df",borderRadius:14,padding:11,gap:8},photoTitle:{fontWeight:"800",color:"#26332d"},cardImage:{width:"100%",height:230,backgroundColor:"#edf0ed",borderRadius:9},button:{backgroundColor:"#173c2e",borderRadius:11,paddingVertical:13,paddingHorizontal:16,alignItems:"center",marginTop:10},secondaryButton:{backgroundColor:"white",borderWidth:1,borderColor:"#bfcac3"},dim:{opacity:.6},buttonText:{color:"white",fontWeight:"800",fontSize:13},secondaryText:{color:"#173c2e"},error:{color:"#9b3a2d",backgroundColor:"#fff0ed",padding:11,borderRadius:9,marginTop:10},disclaimer:{color:"#858b87",fontSize:10,textAlign:"center",marginTop:11},empty:{minHeight:360,alignItems:"center",justifyContent:"center",gap:8},spark:{fontSize:32,color:"#a75d39"},emptyTitle:{fontWeight:"800",color:"#38423d"},report:{marginTop:14},reportHead:{flexDirection:"row",justifyContent:"space-between",gap:12},identity:{flex:1},cardName:{fontSize:27,fontWeight:"800",color:"#18201d",marginBottom:5},grade:{backgroundColor:"#173c2e",borderRadius:14,padding:13,minWidth:105,alignItems:"center"},gradeLabel:{fontSize:9,color:"white"},gradeValue:{fontSize:38,fontWeight:"800",color:"white"},stats:{flexDirection:"row",gap:7,marginVertical:15},stat:{flex:1,backgroundColor:"#f3f5f2",borderRadius:10,padding:10},statValue:{fontSize:12,fontWeight:"800",color:"#26332d"},price:{fontSize:20,fontWeight:"800",color:"#18201d"},blockTitle:{fontSize:13,fontWeight:"800",color:"#26332d"},defect:{flexDirection:"row",gap:9,paddingVertical:9,borderBottomWidth:1,borderBottomColor:"#edf0ed"},dot:{width:8,height:8,borderRadius:4,backgroundColor:"#c5944e",marginTop:4},good:{backgroundColor:"#4d9a72"},defectTitle:{fontSize:12,fontWeight:"800",color:"#26332d"},note:{backgroundColor:"#fff5e9",borderLeftWidth:3,borderLeftColor:"#bd714c",padding:11,borderRadius:8,marginTop:9},greenNote:{backgroundColor:"#edf5f0",borderLeftColor:"#3f775d"},noteTitle:{fontSize:11,fontWeight:"800",color:"#26332d"},noteText:{fontSize:11,color:"#615f5b",marginTop:3},source:{fontSize:9,color:"#858b87",lineHeight:14,marginTop:11},history:{flexDirection:"row",flexWrap:"wrap",gap:9,marginTop:12},historyItem:{minWidth:210,flexGrow:1,flexDirection:"row",justifyContent:"space-between",backgroundColor:"#f3f5f2",borderRadius:10,padding:12},historyRight:{alignItems:"flex-end"},historyGrade:{fontSize:18,fontWeight:"800",color:"#173c2e"},attribution:{fontSize:9,color:"#615f5b",textAlign:"center",backgroundColor:"rgba(255,255,255,.75)",padding:6,borderRadius:8},cameraPage:{flex:1,backgroundColor:"#111a16",padding:20},cameraHeader:{flexDirection:"row",justifyContent:"space-between",alignItems:"center",marginBottom:15},lightKicker:{color:"#d9ff79",fontSize:11,fontWeight:"800",letterSpacing:2},cameraTitle:{color:"white",fontSize:21,fontWeight:"800"},close:{color:"white",fontWeight:"800",padding:10},cameraFrame:{flex:1,borderRadius:16,overflow:"hidden"},guide:{position:"absolute",top:"8%",bottom:"8%",left:"28%",right:"28%",borderWidth:3,borderColor:"#d9ff79",borderRadius:15,alignItems:"center",justifyContent:"flex-end"},guideText:{backgroundColor:"#d9ff79",color:"#173c2e",fontSize:10,fontWeight:"800",padding:6},permission:{flex:1,justifyContent:"center",alignItems:"center",padding:30},permissionText:{color:"white",textAlign:"center"}
});

Object.assign(s, StyleSheet.create({
  guideLayer:{...StyleSheet.absoluteFillObject,alignItems:"center",justifyContent:"center"},
  guide:{width:"42%",maxWidth:390,aspectRatio:2.5/3.5,borderWidth:4,borderColor:"#d9ff79",borderRadius:18,alignItems:"center",justifyContent:"flex-end"},
  aiStatus:{flexDirection:"row",alignItems:"center",gap:9,backgroundColor:"#edf7f0",borderWidth:1,borderColor:"#b9dbc5",borderRadius:10,padding:10,marginVertical:12},
  liveDot:{width:10,height:10,borderRadius:5,backgroundColor:"#25a55f",boxShadow:"0 0 0 4px rgba(37,165,95,.15)"},
  aiLive:{fontSize:10,fontWeight:"900",letterSpacing:1.2,color:"#16713f"},
  phoneBox:{backgroundColor:"#f6f8f6",borderWidth:1,borderColor:"#d6e0d9",borderRadius:12,padding:12,marginBottom:12},phoneTitle:{fontSize:13,fontWeight:"900",color:"#173c2e"},qrRow:{flexDirection:"row",alignItems:"center",gap:12,marginTop:12},qrImage:{width:132,height:132,backgroundColor:"white"},phoneState:{fontWeight:"900",color:"#16713f",marginBottom:6},
  qrLoading:{minHeight:90,flexDirection:"row",alignItems:"center",justifyContent:"center",gap:10},
  mobilePage:{flex:1,backgroundColor:"#eef3ee",padding:18,justifyContent:"center"},mobileCard:{backgroundColor:"white",borderRadius:18,padding:20,gap:14,maxWidth:520,width:"100%",alignSelf:"center"},mobileTitle:{fontSize:27,fontWeight:"900",color:"#18201d"},mobilePicker:{borderWidth:1,borderColor:"#d6e0d9",borderRadius:12,padding:14,gap:9},mobileReady:{color:"#16713f",fontWeight:"800"},mobileSuccess:{color:"#16713f",fontWeight:"800",backgroundColor:"#edf7f0",padding:12,borderRadius:9}
  ,candidateBox:{marginTop:4,marginBottom:14,backgroundColor:"#fffaf0",borderWidth:1,borderColor:"#ead9b8",borderRadius:12,padding:11,gap:7}
  ,candidate:{flexDirection:"row",alignItems:"center",gap:10,borderWidth:1,borderColor:"#e3ddd0",backgroundColor:"white",borderRadius:10,padding:10}
  ,selectedCandidate:{borderColor:"#3f775d",backgroundColor:"#edf5f0"}
  ,selectText:{fontSize:9,fontWeight:"900",letterSpacing:.7,color:"#a75d39"}
  ,loadingScene:{minHeight:360,justifyContent:"center",paddingHorizontal:22}
  ,loadingTrack:{height:54,justifyContent:"center",borderBottomWidth:3,borderBottomColor:"#d8c8aa",marginBottom:17,overflow:"hidden"}
  ,runner:{fontSize:31,width:70}
  ,loadingTitle:{fontSize:18,fontWeight:"900",color:"#26332d",marginBottom:5}
  ,handNote:{alignSelf:"flex-start",marginTop:18,color:"#7b533e",fontSize:13,fontStyle:"italic",backgroundColor:"rgba(255,248,218,.88)",paddingVertical:8,paddingHorizontal:12,borderRadius:5,transform:[{rotate:"-1deg"}]}
}));

export default function App() {
  const sessionId = Platform.OS === "web" && typeof window !== "undefined" ? new URLSearchParams(window.location.search).get("mobile_session") : null;
  return sessionId ? <MobileUpload sessionId={sessionId} /> : <DesktopApp />;
}
