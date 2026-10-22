import { CameraView, useCameraPermissions } from "expo-camera";
import { StatusBar } from "expo-status-bar";
import { useEffect, useRef, useState } from "react";
import { ActivityIndicator, Image, ImageBackground, Modal, Platform, Pressable, SafeAreaView, ScrollView, StyleSheet, Text, View } from "react-native";

const API_URL = process.env.EXPO_PUBLIC_API_URL || "http://localhost:8000";
const sampleCards = {
  "charizard-ex-223": { Front: "/sample_data/charizard-front.png", Back: "/sample_data/card-back.png" },
  "pikachu-160": { Front: "/sample_data/pikachu-front.png", Back: "/sample_data/card-back.png" },
  "umbreon-vmax-215": { Front: "/sample_data/umbreon-front.png", Back: "/sample_data/card-back.png" },
};
const fallbackCards = [{ id: "charizard-ex-223", card_name: "Charizard ex", set_name: "Obsidian Flames", card_number: "223/197" }];

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
      <View style={s.cameraFrame}><CameraView ref={ref} style={StyleSheet.absoluteFill} facing="back" mode="picture" /><View pointerEvents="none" style={s.guide}><Text style={s.guideText}>ALIGN CARD HERE</Text></View></View>
      <Button onPress={snap} disabled={busy}>{busy ? "Capturing…" : `Capture ${side}`}</Button>
    </>}
  </SafeAreaView></Modal>;
}

function Photo({ side, photo, sample, open, clear }) {
  return <View style={s.photo}><Text style={s.photoTitle}>{side}</Text><Image source={{ uri: photo?.uri || sample }} style={s.cardImage} resizeMode="contain" /><Button onPress={open}>Use camera</Button><Button secondary onPress={clear}>Use sample</Button><Text numberOfLines={1} style={s.small}>{photo?.name || "Authentic Pokémon TCG sample image"}</Text></View>;
}

function Report({ data }) {
  if (!data) return <View style={s.empty}><Text style={s.spark}>✦</Text><Text style={s.emptyTitle}>No report yet</Text><Text style={s.muted}>Capture both sides or use the sample, then analyze the card.</Text></View>;
  return <View style={s.report}>
    <View style={s.reportHead}><View style={s.identity}><Text style={s.kicker}>IDENTIFIED CARD</Text><Text style={s.cardName}>{data.card_name}</Text><Text style={s.muted}>{data.set_name} · {data.card_number}{"\n"}{data.variant}</Text></View><View style={s.grade}><Text style={s.gradeLabel}>ESTIMATED</Text><Text style={s.gradeValue}>{data.estimated_grade}</Text><Text style={s.gradeLabel}>Range {data.grade_range}</Text></View></View>
    <View style={s.stats}>{[["Condition", data.condition], ["Confidence", `${Math.round(data.confidence * 100)}%`], ["Centering", data.centering.split(" front")[0]]].map(([a,b]) => <View key={a} style={s.stat}><Text style={s.small}>{a}</Text><Text style={s.statValue}>{b}</Text></View>)}</View>
    <Text style={s.blockTitle}>Visible-defect review</Text>{data.defects.map(d => <View key={d.category} style={s.defect}><View style={[s.dot, d.severity === "none" && s.good]} /><View><Text style={s.defectTitle}>{d.category}</Text><Text style={s.small}>{d.result}</Text></View></View>)}
    <View style={s.stats}><View style={s.stat}><Text style={s.small}>Raw market estimate</Text><Text style={s.price}>${data.raw_market_price.toFixed(2)}</Text></View><View style={s.stat}><Text style={s.small}>Graded estimate</Text><Text style={s.price}>${data.graded_market_price.toFixed(2)}</Text></View></View>
    <View style={s.note}><Text style={s.noteTitle}>Recommendation</Text><Text style={s.noteText}>{data.recommendation}</Text></View><View style={[s.note, s.greenNote]}><Text style={s.noteTitle}>Selling window</Text><Text style={s.noteText}>{data.selling_window}</Text></View>
    <Text style={s.source}>Identification: {data.identification_mode}{"\n"}Pricing: {data.pricing_source}</Text>
  </View>;
}

export default function App() {
  const [photos, setPhotos] = useState({ Front: null, Back: null });
  const [cameraSide, setCameraSide] = useState(null);
  const [cards, setCards] = useState(fallbackCards);
  const [cardId, setCardId] = useState("charizard-ex-223");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const samples = sampleCards[cardId] || sampleCards["charizard-ex-223"];
  useEffect(() => { fetch(`${API_URL}/api/cards`).then(r => r.json()).then(setCards).catch(() => {}); refreshHistory(); }, []);
  async function refreshHistory() { try { const r = await fetch(`${API_URL}/api/assessments`); if (r.ok) setHistory(await r.json()); } catch {} }
  async function appendPhoto(form, key, photo, sample) {
    if (Platform.OS === "web") { const response = await fetch(photo?.uri || sample); form.append(key, await response.blob(), photo?.name || `sample_${key}.svg`); }
    else if (photo) form.append(key, { uri: photo.uri, name: photo.name, type: photo.type });
    else throw new Error(`Capture the card ${key} before analyzing on a phone.`);
  }
  async function analyze() {
    setLoading(true); setError(""); setResult(null);
    try {
      const form = new FormData(); await appendPhoto(form, "front", photos.Front, samples.Front); await appendPhoto(form, "back", photos.Back, samples.Back); form.append("card_id", cardId);
      const response = await fetch(`${API_URL}/api/assessments`, { method: "POST", body: form }); const body = await response.json(); if (!response.ok) throw new Error(body.detail || "Analysis failed.");
      setResult(body); await refreshHistory();
    } catch (e) { setError(e.message || "Cannot reach the DeckFlow API."); } finally { setLoading(false); }
  }
  return <ImageBackground source={{ uri: "/sample_data/library-background.webp" }} style={s.background} imageStyle={s.backgroundImage} resizeMode="cover"><SafeAreaView style={s.safe}><StatusBar style="dark" />{cameraSide && <Camera side={cameraSide} close={() => setCameraSide(null)} captured={p => { setPhotos(old => ({ ...old, [cameraSide]: p })); setCameraSide(null); }} />}
    <ScrollView contentContainerStyle={s.page}>
      <View style={s.header}><View style={s.brand}><View style={s.logo}><Text style={s.logoText}>DF</Text></View><View><Text style={s.brandTitle}>DeckFlow</Text><Text style={s.small}>React Native card pre-grading</Text></View></View><View style={s.badge}><Text style={s.badgeText}>CPSC 490 Demo</Text></View></View>
      <View style={s.hero}><Text style={s.kicker}>SCAN. ASSESS. DECIDE.</Text><Text style={s.heroTitle}>Turn card images into a clear assessment report.</Text><Text style={s.heroCopy}>Capture the front and back, confirm the card, and generate an unofficial grade, defect summary, and market estimate.</Text></View>
      <View style={s.grid}><View style={s.panel}><Text style={s.step}>01 · CARD CAPTURE</Text><Text style={s.panelTitle}>Front and back images</Text><Text style={s.muted}>Confirm one of the supported demo cards.</Text>
        <View style={s.choices}>{cards.map(c => <Pressable key={c.id} onPress={() => { setCardId(c.id); setPhotos({ Front:null, Back:null }); setResult(null); }} style={[s.choice, cardId === c.id && s.activeChoice]}><Text style={s.choiceTitle}>{c.card_name}</Text><Text style={s.small}>{c.set_name} · {c.card_number}</Text></Pressable>)}</View>
        <View style={s.photos}><Photo side="Front" photo={photos.Front} sample={samples.Front} open={() => setCameraSide("Front")} clear={() => setPhotos(o => ({...o, Front:null}))} /><Photo side="Back" photo={photos.Back} sample={samples.Back} open={() => setCameraSide("Back")} clear={() => setPhotos(o => ({...o, Back:null}))} /></View>
        <Button onPress={analyze} disabled={loading}>{loading ? "Analyzing…" : "Analyze card"}</Button>{error ? <Text accessibilityRole="alert" style={s.error}>{error}</Text> : null}<Text style={s.disclaimer}>Unofficial estimate only. DeckFlow does not replace professional grading.</Text>
      </View><View style={s.panel}><Text style={s.step}>02 · ASSESSMENT</Text><Text style={s.panelTitle}>{result ? `Report ${result.assessment_id}` : "Assessment report"}</Text>{loading ? <View style={s.empty}><ActivityIndicator size="large" color="#173c2e" /><Text style={s.emptyTitle}>Analyzing card</Text></View> : <Report data={result} />}</View></View>
      <View style={s.panel}><Text style={s.step}>03 · HISTORY</Text><Text style={s.panelTitle}>Recent assessments</Text>{history.length ? <View style={s.history}>{history.map(x => <Pressable key={x.created_at} onPress={() => setResult(x)} style={s.historyItem}><View><Text style={s.choiceTitle}>{x.card_name}</Text><Text style={s.small}>{x.set_name} · {x.card_number}</Text></View><View style={s.historyRight}><Text style={s.historyGrade}>{x.estimated_grade}</Text><Text style={s.small}>${x.raw_market_price.toFixed(2)} raw</Text></View></Pressable>)}</View> : <Text style={s.muted}>No assessments saved in this session.</Text>}</View>
      <Text style={s.attribution}>Background artwork: “Let's Find Pokémon! – Library” by Kazunori Aihara · Classroom prototype use</Text>
    </ScrollView></SafeAreaView></ImageBackground>;
}

const s = StyleSheet.create({background:{flex:1,backgroundColor:"#f3ead8"},backgroundImage:{opacity:.34},safe:{flex:1,backgroundColor:"rgba(250,247,239,.72)"},page:{width:"100%",maxWidth:1220,alignSelf:"center",padding:24,gap:20},header:{flexDirection:"row",justifyContent:"space-between",alignItems:"center"},brand:{flexDirection:"row",alignItems:"center",gap:12},logo:{width:48,height:48,borderRadius:12,backgroundColor:"#173c2e",alignItems:"center",justifyContent:"center"},logoText:{color:"white",fontWeight:"800"},brandTitle:{fontSize:20,fontWeight:"800",color:"#18201d"},badge:{backgroundColor:"rgba(223,232,223,.94)",paddingVertical:8,paddingHorizontal:12,borderRadius:30},badgeText:{color:"#24533e",fontSize:12,fontWeight:"800"},hero:{maxWidth:760,paddingVertical:26},kicker:{color:"#a75d39",letterSpacing:2,fontSize:11,fontWeight:"800",marginBottom:10},heroTitle:{fontSize:46,lineHeight:49,fontWeight:"700",color:"#18201d",marginBottom:14},heroCopy:{fontSize:16,lineHeight:25,color:"#4f5853"},grid:{flexDirection:"row",gap:20,alignItems:"flex-start",flexWrap:"wrap"},panel:{backgroundColor:"rgba(255,255,255,.94)",borderRadius:18,padding:24,minWidth:320,flexGrow:1,flexBasis:480,boxShadow:"0 12px 38px rgba(36,57,47,.14)"},step:{color:"#a75d39",fontSize:11,fontWeight:"800",letterSpacing:1},panelTitle:{fontSize:19,fontWeight:"800",color:"#18201d",marginVertical:6},muted:{color:"#747d78",fontSize:13,lineHeight:19},small:{color:"#7c8580",fontSize:11},choices:{gap:8,marginVertical:16},choice:{borderWidth:1,borderColor:"#dfe4df",borderRadius:10,padding:10},activeChoice:{backgroundColor:"#eaf2ed",borderColor:"#35664f"},choiceTitle:{fontWeight:"800",color:"#26332d"},photos:{flexDirection:"row",gap:12,flexWrap:"wrap"},photo:{flex:1,minWidth:175,borderWidth:1,borderColor:"#dfe4df",borderRadius:14,padding:11,gap:8},photoTitle:{fontWeight:"800",color:"#26332d"},cardImage:{width:"100%",height:230,backgroundColor:"#edf0ed",borderRadius:9},button:{backgroundColor:"#173c2e",borderRadius:11,paddingVertical:13,paddingHorizontal:16,alignItems:"center",marginTop:10},secondaryButton:{backgroundColor:"white",borderWidth:1,borderColor:"#bfcac3"},dim:{opacity:.6},buttonText:{color:"white",fontWeight:"800",fontSize:13},secondaryText:{color:"#173c2e"},error:{color:"#9b3a2d",backgroundColor:"#fff0ed",padding:11,borderRadius:9,marginTop:10},disclaimer:{color:"#858b87",fontSize:10,textAlign:"center",marginTop:11},empty:{minHeight:360,alignItems:"center",justifyContent:"center",gap:8},spark:{fontSize:32,color:"#a75d39"},emptyTitle:{fontWeight:"800",color:"#38423d"},report:{marginTop:14},reportHead:{flexDirection:"row",justifyContent:"space-between",gap:12},identity:{flex:1},cardName:{fontSize:27,fontWeight:"800",color:"#18201d",marginBottom:5},grade:{backgroundColor:"#173c2e",borderRadius:14,padding:13,minWidth:105,alignItems:"center"},gradeLabel:{fontSize:9,color:"white"},gradeValue:{fontSize:38,fontWeight:"800",color:"white"},stats:{flexDirection:"row",gap:7,marginVertical:15},stat:{flex:1,backgroundColor:"#f3f5f2",borderRadius:10,padding:10},statValue:{fontSize:12,fontWeight:"800",color:"#26332d"},price:{fontSize:20,fontWeight:"800",color:"#18201d"},blockTitle:{fontSize:13,fontWeight:"800",color:"#26332d"},defect:{flexDirection:"row",gap:9,paddingVertical:9,borderBottomWidth:1,borderBottomColor:"#edf0ed"},dot:{width:8,height:8,borderRadius:4,backgroundColor:"#c5944e",marginTop:4},good:{backgroundColor:"#4d9a72"},defectTitle:{fontSize:12,fontWeight:"800",color:"#26332d"},note:{backgroundColor:"#fff5e9",borderLeftWidth:3,borderLeftColor:"#bd714c",padding:11,borderRadius:8,marginTop:9},greenNote:{backgroundColor:"#edf5f0",borderLeftColor:"#3f775d"},noteTitle:{fontSize:11,fontWeight:"800",color:"#26332d"},noteText:{fontSize:11,color:"#615f5b",marginTop:3},source:{fontSize:9,color:"#858b87",lineHeight:14,marginTop:11},history:{flexDirection:"row",flexWrap:"wrap",gap:9,marginTop:12},historyItem:{minWidth:210,flexGrow:1,flexDirection:"row",justifyContent:"space-between",backgroundColor:"#f3f5f2",borderRadius:10,padding:12},historyRight:{alignItems:"flex-end"},historyGrade:{fontSize:18,fontWeight:"800",color:"#173c2e"},attribution:{fontSize:9,color:"#615f5b",textAlign:"center",backgroundColor:"rgba(255,255,255,.75)",padding:6,borderRadius:8},cameraPage:{flex:1,backgroundColor:"#111a16",padding:20},cameraHeader:{flexDirection:"row",justifyContent:"space-between",alignItems:"center",marginBottom:15},lightKicker:{color:"#d9ff79",fontSize:11,fontWeight:"800",letterSpacing:2},cameraTitle:{color:"white",fontSize:21,fontWeight:"800"},close:{color:"white",fontWeight:"800",padding:10},cameraFrame:{flex:1,borderRadius:16,overflow:"hidden"},guide:{position:"absolute",top:"8%",bottom:"8%",left:"28%",right:"28%",borderWidth:3,borderColor:"#d9ff79",borderRadius:15,alignItems:"center",justifyContent:"flex-end"},guideText:{backgroundColor:"#d9ff79",color:"#173c2e",fontSize:10,fontWeight:"800",padding:6},permission:{flex:1,justifyContent:"center",alignItems:"center",padding:30},permissionText:{color:"white",textAlign:"center"}
});
