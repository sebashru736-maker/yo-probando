import React, { useLayoutEffect, useMemo } from "react";
import {
  AbsoluteFill,
  Easing,
  Img,
  Interactive,
  interpolate,
  spring,
  staticFile,
  Track,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Audio, Video } from "@remotion/media";
import { ThreeCanvas } from "@remotion/three";
import { loadFont } from "@remotion/fonts";
import { useThree } from "@react-three/fiber";
import * as THREE from "three";
import { FontLoader } from "three/examples/jsm/loaders/FontLoader.js";
import { TextGeometry } from "three/examples/jsm/geometries/TextGeometry.js";
import { SVGLoader } from "three/examples/jsm/loaders/SVGLoader.js";
import fontData from "../public/helvetiker_bold.typeface.json";
import { HBO_SVG } from "./hbo-logo";

loadFont({
  family: "Tzubaru Display",
  url: staticFile("DejaVuSansCondensed-Bold.ttf"),
  weight: "700",
});
loadFont({
  family: "Tzubaru Sans",
  url: staticFile("DejaVuSans.ttf"),
  weight: "400",
});

const GOLD = "#efbe75";
const BLUE = "#3a72ff";
const INK = "#030713";
const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

const CameraRig: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { camera } = useThree();
  useLayoutEffect(() => {
    camera.position.set(
      Math.sin((frame / fps) * 0.3) * 0.26,
      0.55 + Math.cos((frame / fps) * 0.4) * 0.12,
      9.9 - Math.min(frame / fps, 8) * 0.09,
    );
    camera.lookAt(0, 0.0, 0);
    camera.updateProjectionMatrix();
  }, [camera, frame, fps]);
  return null;
};

const PortalWorld: React.FC<{ ending?: boolean }> = ({ ending = false }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const time = frame / fps;
  const reveal = spring({ frame, fps, config: { damping: 24, stiffness: 75 } });
  const geo = useMemo(() => {
    const font = new FontLoader().parse(fontData);
    const geometry = new TextGeometry("max", {
      font,
      size: 1.3,
      depth: 0.2,
      curveSegments: 10,
      bevelEnabled: true,
      bevelThickness: 0.018,
      bevelSize: 0.012,
      bevelSegments: 3,
    });
    geometry.center();
    return geometry;
  }, []);
  const hboGeo = useMemo(() => {
    const paths = new SVGLoader().parse(HBO_SVG).paths;
    const shapes = paths.flatMap((path) => SVGLoader.createShapes(path));
    const geometry = new THREE.ExtrudeGeometry(shapes, {
      depth: 1.0,
      bevelEnabled: true,
      bevelSize: 0.04,
      bevelThickness: 0.04,
      bevelSegments: 2,
      curveSegments: 12,
    });
    geometry.scale(0.145, -0.145, 0.18);
    geometry.center();
    return geometry;
  }, []);
  const stars = useMemo(() => {
    const positions = new Float32Array(900 * 3);
    const colors = new Float32Array(900 * 3);
    let seed = 736;
    const random = () => {
      seed = (seed * 16807) % 2147483647;
      return (seed - 1) / 2147483646;
    };
    for (let i = 0; i < 900; i++) {
      positions[i * 3] = (random() - 0.5) * 20;
      positions[i * 3 + 1] = (random() - 0.5) * 24;
      positions[i * 3 + 2] = -2 - random() * 14;
      const c = new THREE.Color(i % 3 === 0 ? GOLD : "#8cbcff");
      colors[i * 3] = c.r;
      colors[i * 3 + 1] = c.g;
      colors[i * 3 + 2] = c.b;
    }
    return { positions, colors };
  }, []);
  return (
    <>
      <CameraRig />
      <ambientLight intensity={0.7} color="#a7bbff" />
      <directionalLight position={[3, 4, 6]} intensity={5.5} color="#fff1d4" />
      <pointLight
        position={[-4, 0, 3]}
        intensity={85}
        color={BLUE}
        distance={20}
      />
      <pointLight
        position={[4, -2, 2]}
        intensity={75}
        color={GOLD}
        distance={20}
      />
      <pointLight
        position={[0, 4, -1]}
        intensity={45}
        color="#88caff"
        distance={15}
      />
      <points rotation={[0, time * 0.018, time * 0.009]}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            args={[stars.positions, 3]}
          />
          <bufferAttribute attach="attributes-color" args={[stars.colors, 3]} />
        </bufferGeometry>
        <pointsMaterial
          size={0.026}
          vertexColors
          transparent
          opacity={0.7}
          sizeAttenuation
          depthWrite={false}
          blending={THREE.AdditiveBlending}
        />
      </points>
      <group position={[0, 0.95, 0]} scale={0.72 * (0.75 + reveal * 0.25)}>
        <group
          rotation={[
            0.19 + Math.sin(time * 0.4) * 0.12,
            Math.sin(time * 0.36) * 0.27,
            time * 0.12,
          ]}
        >
          <mesh>
            <torusGeometry args={[2.45, 0.073, 12, 120]} />
            <meshStandardMaterial
              color={GOLD}
              metalness={0.78}
              roughness={0.23}
              emissive="#8f4915"
              emissiveIntensity={0.13}
            />
          </mesh>
          <mesh rotation={[0, 0, 0.3]}>
            <torusGeometry args={[2.61, 0.016, 8, 120, Math.PI * 1.7]} />
            <meshBasicMaterial color="#ffe0a5" />
          </mesh>
          <mesh rotation={[0, 0, Math.PI]}>
            <torusGeometry args={[2.32, 0.012, 8, 120, Math.PI * 1.25]} />
            <meshBasicMaterial color="#fff1d0" />
          </mesh>
        </group>
        <group rotation={[-0.47, -0.35, -time * 0.19]}>
          <mesh>
            <torusGeometry args={[3.15, 0.027, 8, 120, Math.PI * 1.45]} />
            <meshStandardMaterial
              color="#558bff"
              emissive="#1e4fc9"
              emissiveIntensity={0.8}
              metalness={0.6}
              roughness={0.25}
            />
          </mesh>
          <mesh rotation={[0, 0, 2.7]}>
            <torusGeometry args={[3.26, 0.012, 8, 100, Math.PI * 0.65]} />
            <meshBasicMaterial color="#8ecaff" />
          </mesh>
        </group>
        <group rotation={[0.2, -0.1, time * 0.12]}>
          {Array.from({ length: 20 }, (_, i) => {
            const a = (i / 20) * Math.PI * 2;
            return (
              <mesh
                key={i}
                position={[
                  Math.cos(a) * 2.9,
                  Math.sin(a) * 2.9,
                  Math.sin(a * 2) * 0.22,
                ]}
                rotation={[a, 0.3, -a]}
                scale={[0.025, i % 5 === 0 ? 0.24 : 0.1, 0.045]}
              >
                <boxGeometry />
                <meshStandardMaterial
                  color={i % 5 === 0 ? GOLD : "#6c99e7"}
                  metalness={0.6}
                  roughness={0.3}
                />
              </mesh>
            );
          })}
        </group>
        {!ending && (
          <group
            rotation={[-0.03, Math.sin(time * 0.35) * 0.07, 0]}
            scale={0.85 + reveal * 0.15}
          >
            <mesh geometry={hboGeo} position={[0, 0.72, 0.32]}>
              <meshStandardMaterial
                color="#f3f6ff"
                metalness={0.42}
                roughness={0.23}
                emissive="#20335b"
                emissiveIntensity={0.22}
              />
            </mesh>
            <mesh geometry={geo} position={[0, -0.72, 0.32]}>
              <meshStandardMaterial
                color="#f3f6ff"
                metalness={0.42}
                roughness={0.23}
                emissive="#20335b"
                emissiveIntensity={0.22}
              />
            </mesh>
          </group>
        )}
      </group>
      <group rotation={[time * 0.012, time * 0.025, -0.15]}>
        {Array.from({ length: 14 }, (_, i) => {
          const a = (i / 14) * Math.PI * 2;
          return (
            <mesh
              key={i}
              position={[
                Math.cos(a) * 5.4,
                Math.sin(a) * 7,
                -2.5 + Math.sin(a) * 2,
              ]}
              rotation={[a * 0.4, a + time * 0.1, a * 0.3]}
            >
              <boxGeometry args={[0.42, 0.75, 0.045]} />
              <meshStandardMaterial
                color={i % 2 ? "#0f2351" : "#705032"}
                metalness={0.75}
                roughness={0.2}
                transparent
                opacity={0.75}
              />
            </mesh>
          );
        })}
      </group>
    </>
  );
};

const SceneBase: React.FC<React.PropsWithChildren<{ ending?: boolean }>> = ({
  children,
  ending,
}) => {
  const { width, height } = useVideoConfig();
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill
      style={{
        backgroundColor: INK,
        color: "#fff",
        fontFamily: "Tzubaru Sans",
        overflow: "hidden",
      }}
    >
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse at 35% 40%, #142a57 0%, #090d21 35%, #02040d 72%)",
        }}
      />
      <ThreeCanvas
        name="Portal tridimensional"
        width={width}
        height={height}
        camera={{ fov: 47, near: 0.1, far: 100 }}
        dpr={1}
        gl={{
          antialias: true,
          alpha: true,
          powerPreference: "high-performance",
        }}
        style={{ opacity: ending ? 0.38 : 1 }}
      >
        <PortalWorld ending={ending} />
      </ThreeCanvas>
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(0deg, #02040df5 0%, transparent 43%, transparent 78%, #02040d88 100%)",
        }}
      />
      <AbsoluteFill
        style={{
          opacity: interpolate(frame, [0, 12], [1, 0], CLAMP),
          backgroundColor: "#02040d",
          pointerEvents: "none",
        }}
      />
      {children}
    </AbsoluteFill>
  );
};

const AnimatedLine: React.FC<{
  text: string;
  delay?: number;
  size?: number;
  color?: string;
}> = ({ text, delay = 0, size = 108, color = "#ffffff" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div
      style={{
        fontFamily: "Tzubaru Display",
        fontSize: size,
        fontWeight: 700,
        lineHeight: 1.02,
        letterSpacing: -3,
        color,
        whiteSpace: "nowrap",
      }}
    >
      {text.split(" ").map((word, i) => (
        <span
          key={`${word}-${i}`}
          style={{
            display: "inline-block",
            marginRight: 22,
            opacity: interpolate(frame - delay - i * 3, [0, 9], [0, 1], CLAMP),
            translate: `0 ${interpolate(spring({ frame: frame - delay - i * 3, fps, config: { damping: 23, stiffness: 115 } }), [0, 1], [60, 0])}px`,
          }}
        >
          {word}
        </span>
      ))}
    </div>
  );
};

const OpeningInner: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <SceneBase>
      <div
        style={{
          position: "absolute",
          top: 102,
          left: 88,
          right: 88,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div
          style={{
            fontFamily: "Tzubaru Display",
            fontSize: 42,
            letterSpacing: -1,
          }}
        >
          tzubaru
        </div>
        <div style={{ fontSize: 24, color: "#c2ccdf" }}>Presenta</div>
      </div>
      <div
        style={{
          position: "absolute",
          left: 88,
          right: 70,
          top: 1250,
          opacity: interpolate(frame, [0, 15, 102, 116], [0, 1, 1, 0], CLAMP),
        }}
      >
        <AnimatedLine text="HAY" delay={16} size={132} />
        <AnimatedLine text="HISTORIAS." delay={22} size={132} />
        <div
          style={{
            marginTop: 33,
            fontSize: 36,
            color: "#c6d1e3",
            opacity: interpolate(frame, [38, 55], [0, 1], CLAMP),
          }}
        >
          Y luego están las que se quedan contigo.
        </div>
      </div>
      <div
        style={{
          position: "absolute",
          left: 88,
          right: 70,
          top: 1250,
          opacity: interpolate(
            frame,
            [116, 124, 232, 239],
            [0, 1, 1, 0],
            CLAMP,
          ),
        }}
      >
        <AnimatedLine text="QUE SE" delay={119} size={132} />
        <AnimatedLine text="VIVEN." delay={125} size={146} color={GOLD} />
        <div
          style={{
            marginTop: 33,
            fontSize: 36,
            color: "#c6d1e3",
            opacity: interpolate(frame, [145, 160], [0, 1], CLAMP),
          }}
        >
          Dale play a algo extraordinario.
        </div>
      </div>
      <div
        style={{
          position: "absolute",
          bottom: 118,
          left: 88,
          right: 88,
          height: 2,
          background: "#ffffff18",
        }}
      >
        <div
          style={{
            height: 2,
            background: GOLD,
            width: `${interpolate(frame, [0, 8 * fps], [0, 100], CLAMP)}%`,
          }}
        />
      </div>
      <div
        style={{
          position: "absolute",
          bottom: 72,
          left: 88,
          fontSize: 18,
          color: "#8794b1",
        }}
      >
        Dirección de arte · Avance de apertura
      </div>
    </SceneBase>
  );
};

const EndInner: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  return (
    <SceneBase ending>
      <div
        style={{
          position: "absolute",
          top: 180,
          left: 0,
          right: 0,
          textAlign: "center",
          fontSize: 35,
          color: "#cbd5e6",
          opacity: interpolate(frame, [8, 28], [0, 1], CLAMP),
        }}
      >
        Tu próxima gran historia empieza aquí.
      </div>
      <Img
        src={staticFile("tzubaru.png")}
        style={{
          position: "absolute",
          width: 800,
          height: 800,
          objectFit: "contain",
          left: 140,
          top: 470,
          scale: interpolate(
            spring({
              frame: frame - 4,
              fps,
              config: { damping: 24, stiffness: 90 },
            }),
            [0, 1],
            [0.86, 1],
          ),
          opacity: interpolate(frame, [4, 20], [0, 1], CLAMP),
        }}
      />
      <div
        style={{
          position: "absolute",
          top: 1370,
          left: 88,
          right: 88,
          textAlign: "center",
          opacity: interpolate(frame, [28, 43], [0, 1], CLAMP),
        }}
      >
        <div
          style={{
            fontFamily: "Tzubaru Display",
            fontSize: 72,
            letterSpacing: -2,
          }}
        >
          Dale play a lo grande.
        </div>
        <div style={{ fontSize: 36, color: GOLD, marginTop: 28 }}>HBO Max</div>
      </div>
      <AbsoluteFill
        style={{
          backgroundColor: INK,
          opacity: interpolate(
            frame,
            [durationInFrames - 14, durationInFrames - 1],
            [0, 1],
            CLAMP,
          ),
          pointerEvents: "none",
        }}
      />
    </SceneBase>
  );
};

export const OpeningScene = Interactive.create({
  Component: OpeningInner,
  layout: "absolute-fill",
});
export const EndScene = Interactive.create({
  Component: EndInner,
  layout: "absolute-fill",
});

export const Avance3D: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill>
      <Track name="Piezas tridimensionales">
        <OpeningScene
          name="Apertura cinematográfica"
          durationInFrames={8 * fps}
        />
        <EndScene
          name="Cierre de marca"
          from={8 * fps}
          durationInFrames={4 * fps}
        />
      </Track>
      <Audio
        name="Música y diseño sonoro sincronizados"
        src={staticFile("audio/avance-master.wav")}
      />
    </AbsoluteFill>
  );
};

const FilmInner: React.FC<{ src: string; title: string; eyebrow: string }> = ({
  src,
  title,
  eyebrow,
}) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill
      style={{ background: INK, fontFamily: "Tzubaru Sans", color: "white" }}
    >
      <Video
        src={staticFile(src)}
        muted
        objectFit="cover"
        style={{ width: "100%", height: "100%" }}
      />
      <AbsoluteFill
        style={{
          background: "linear-gradient(0deg, #02040dee, transparent 60%)",
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 88,
          right: 88,
          bottom: 160,
          opacity: interpolate(frame, [5, 18], [0, 1], {
            ...CLAMP,
            easing: Easing.out(Easing.cubic),
          }),
        }}
      >
        <div style={{ fontSize: 32, color: GOLD, marginBottom: 25 }}>
          {eyebrow}
        </div>
        <AnimatedLine text={title} size={78} delay={8} />
      </div>
    </AbsoluteFill>
  );
};
const FilmScene = Interactive.create({
  Component: FilmInner,
  layout: "absolute-fill",
});

export const FinalConClips: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill>
      <Track name="Montaje de material oficial">
        <OpeningScene name="Apertura" durationInFrames={3 * fps} />
        <FilmScene
          name="Ciencia ficción"
          from={3 * fps}
          durationInFrames={8 * fps}
          src="clips/dune.mp4"
          title="DUNE: PARTE DOS"
          eyebrow="Universos que te atrapan"
        />
        <FilmScene
          name="Acción"
          from={11 * fps}
          durationInFrames={7 * fps}
          src="clips/batman.mp4"
          title="THE BATMAN"
          eyebrow="Cada decisión lo cambia todo"
        />
        <FilmScene
          name="Fantasía"
          from={18 * fps}
          durationInFrames={7 * fps}
          src="clips/dragon.mp4"
          title="LA CASA DEL DRAGÓN"
          eyebrow="Batallas por las que lo darías todo"
        />
        <EndScene name="Tzubaru" from={25 * fps} durationInFrames={7 * fps} />
      </Track>
      <Audio
        name="Master cinematográfico"
        src={staticFile("audio/final-master.wav")}
      />
    </AbsoluteFill>
  );
};
